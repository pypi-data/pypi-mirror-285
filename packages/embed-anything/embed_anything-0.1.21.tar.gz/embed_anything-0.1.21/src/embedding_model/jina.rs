#[cfg(feature = "mkl")]
extern crate intel_mkl_src;

#[cfg(feature = "accelerate")]
extern crate accelerate_src;

use std::collections::HashMap;

use crate::file_processor::audio::audio_processor::Segment;

use super::embed::{AudioEmbed, Embed, EmbedData, TextEmbed};
use anyhow::Error as E;
use candle_core::{DType, Device, Tensor};
use candle_nn::{Module, VarBuilder};
use candle_transformers::models::jina_bert::{BertModel, Config};
use hf_hub::{Repo, RepoType};
use tokenizers::Tokenizer;
pub struct JinaEmbeder {
    pub model: BertModel,
    pub tokenizer: Tokenizer,
}

impl Default for JinaEmbeder {
    fn default() -> Self {
        let api = hf_hub::api::sync::Api::new().unwrap();
        let model_file = api
            .repo(Repo::new(
                "jinaai/jina-embeddings-v2-base-en".to_string(),
                RepoType::Model,
            ))
            .get("model.safetensors")
            .unwrap();
        let config = Config::v2_base();

        let device = Device::Cpu;
        let vb = unsafe {
            VarBuilder::from_mmaped_safetensors(&[model_file.clone()], DType::F32, &device).unwrap()
        };
        let model = BertModel::new(vb, &config).unwrap();
        let mut tokenizer = Self::get_tokenizer(None).unwrap();
        let pp = tokenizers::PaddingParams {
            strategy: tokenizers::PaddingStrategy::BatchLongest,
            ..Default::default()
        };
        tokenizer.with_padding(Some(pp));
        JinaEmbeder { model, tokenizer }
    }
}

impl JinaEmbeder {
    pub fn get_tokenizer(tokenizer: Option<String>) -> anyhow::Result<Tokenizer> {
        let tokenizer = match tokenizer {
            None => {
                let api = hf_hub::api::sync::Api::new()?;
                let api = api.repo(Repo::new(
                    "sentence-transformers/all-MiniLM-L6-v2".to_string(),
                    RepoType::Model,
                ));
                api.get("tokenizer.json")?
            }
            Some(file) => file.into(),
        };

        Tokenizer::from_file(tokenizer).map_err(E::msg)
    }

    pub fn tokenize_batch(&self, text_batch: &[String], device: &Device) -> anyhow::Result<Tensor> {
        let tokens = self
            .tokenizer
            .encode_batch(text_batch.to_vec(), true)
            .map_err(E::msg)?;
        let token_ids = tokens
            .iter()
            .map(|tokens| {
                let tokens = tokens.get_ids().to_vec();
                Tensor::new(tokens.as_slice(), device)
            })
            .collect::<candle_core::Result<Vec<_>>>()?;
        Ok(Tensor::stack(&token_ids, 0)?)
    }

    fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        let token_ids = self.tokenize_batch(text_batch, &self.model.device).unwrap();
        let embeddings = self.model.forward(&token_ids).unwrap();

        let (_n_sentence, n_tokens, _hidden_size) = embeddings.dims3().unwrap();

        let embeddings = (embeddings.sum(1).unwrap() / (n_tokens as f64)).unwrap();
        let embeddings = normalize_l2(&embeddings).unwrap();

        let encodings = embeddings.to_vec2::<f32>().unwrap();
        let final_embeddings = encodings
            .iter()
            .zip(text_batch)
            .map(|(data, text)| EmbedData::new(data.to_vec(), Some(text.clone()), metadata.clone()))
            .collect::<Vec<_>>();
        Ok(final_embeddings)
    }

    fn embed_audio<T: AsRef<std::path::Path>>(
        &self,
        segments: Vec<Segment>,
        audio_file: T,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        let text_batch = segments
            .iter()
            .map(|segment| segment.dr.text.clone())
            .collect::<Vec<String>>();

        let token_ids = self
            .tokenize_batch(&text_batch, &self.model.device)
            .unwrap();
        println!("{:?}", token_ids);
        let token_type_ids = token_ids.zeros_like().unwrap();
        let embeddings = self.model.forward(&token_ids).unwrap();
        let (_n_sentence, n_tokens, _hidden_size) = embeddings.dims3().unwrap();
        let embeddings = (embeddings.sum(1).unwrap() / (n_tokens as f64)).unwrap();
        let embeddings = normalize_l2(&embeddings).unwrap();
        let encodings = embeddings.to_vec2::<f32>().unwrap();
        let final_embeddings = encodings
            .iter()
            .enumerate()
            .map(|(i, data)| {
                let mut metadata = HashMap::new();
                metadata.insert("start".to_string(), segments[i].start.to_string());
                metadata.insert(
                    "end".to_string(),
                    (segments[i].start + segments[i].duration).to_string(),
                );
                metadata.insert(
                    "file_name".to_string(),
                    (audio_file.as_ref().to_str().unwrap()).to_string(),
                );
                EmbedData::new(data.to_vec(), Some(text_batch[i].clone()), Some(metadata))
            })
            .collect::<Vec<_>>();
        Ok(final_embeddings)
    }
}


impl Embed for JinaEmbeder {
    fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        self.embed(text_batch, metadata)
    }
}

impl TextEmbed for JinaEmbeder {
    fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        self.embed(text_batch, metadata)
    }
}

impl AudioEmbed for JinaEmbeder {
    fn embed_audio<T: AsRef<std::path::Path>>(
        &self,
        segments: Vec<Segment>,
        audio_file: T,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        self.embed_audio(segments, audio_file)
    }
}

pub fn normalize_l2(v: &Tensor) -> candle_core::Result<Tensor> {
    v.broadcast_div(&v.sqr()?.sum_keepdim(1)?.sqrt()?)
}
