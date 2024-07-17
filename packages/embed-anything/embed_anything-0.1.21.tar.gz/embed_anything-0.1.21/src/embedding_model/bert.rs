#[cfg(feature = "mkl")]
extern crate intel_mkl_src;

#[cfg(feature = "accelerate")]
extern crate accelerate_src;

use std::collections::HashMap;

use crate::file_processor::audio::audio_processor::Segment;

use super::embed::{AudioEmbed, Embed, EmbedData, TextEmbed};
use anyhow::Error as E;
use candle_core::{Device, Tensor};
use candle_nn::VarBuilder;
use candle_transformers::models::bert::{BertModel, Config, HiddenAct, DTYPE};
use hf_hub::{api::sync::Api, Repo};
use tokenizers::{PaddingParams, Tokenizer};

pub struct BertEmbeder {
    pub model: BertModel,
    pub tokenizer: Tokenizer,
}

impl Default for BertEmbeder {
    fn default() -> Self {
        let device = Device::Cpu;
        let default_model = "sentence-transformers/all-MiniLM-L12-v2".to_string();
        let default_revision = "refs/pr/21".to_string();
        let (model_id, _revision) = (default_model, default_revision);
        let repo = Repo::model(model_id);
        let (config_filename, tokenizer_filename, weights_filename) = {
            let api = Api::new().unwrap();
            let api = api.repo(repo);
            let config = api.get("config.json").unwrap();
            let tokenizer = api.get("tokenizer.json").unwrap();
            let weights = api.get("model.safetensors").unwrap();

            (config, tokenizer, weights)
        };
        let config = std::fs::read_to_string(config_filename).unwrap();
        let mut config: Config = serde_json::from_str(&config).unwrap();
        let mut tokenizer = Tokenizer::from_file(tokenizer_filename)
            .map_err(E::msg)
            .unwrap();

        let pp = PaddingParams {
            strategy: tokenizers::PaddingStrategy::BatchLongest,
            ..Default::default()
        };
        tokenizer.with_padding(Some(pp));

        let vb = unsafe {
            VarBuilder::from_mmaped_safetensors(&[weights_filename], DTYPE, &device).unwrap()
        };

        config.hidden_act = HiddenAct::GeluApproximate;

        let model = BertModel::load(vb, &config).unwrap();
        BertEmbeder { model, tokenizer }
    }
}
impl BertEmbeder {
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

    pub fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        let token_ids = self.tokenize_batch(text_batch, &self.model.device).unwrap();
        let token_type_ids = token_ids.zeros_like().unwrap();
        let embeddings = self.model.forward(&token_ids, &token_type_ids).unwrap();
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
        let token_type_ids = token_ids.zeros_like().unwrap();
        let embeddings = self.model.forward(&token_ids, &token_type_ids).unwrap();
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

impl Embed for BertEmbeder {
    fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        self.embed(text_batch, metadata)
    }
}

impl TextEmbed for BertEmbeder {
    fn embed(
        &self,
        text_batch: &[String],
        metadata: Option<HashMap<String, String>>,
    ) -> Result<Vec<EmbedData>, anyhow::Error> {
        self.embed(text_batch, metadata)
    }
}

impl AudioEmbed for BertEmbeder {
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
