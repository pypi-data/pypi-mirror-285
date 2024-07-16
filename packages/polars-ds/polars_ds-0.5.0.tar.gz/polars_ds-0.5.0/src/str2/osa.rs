use crate::utils::split_offsets;
use polars::prelude::{arity::binary_elementwise_values, *};
use pyo3_polars::{
    derive::{polars_expr, CallerContext},
    export::polars_core::{
        utils::rayon::prelude::{IntoParallelIterator, ParallelIterator},
        POOL,
    },
};
use rapidfuzz::distance::osa;

#[inline(always)]
fn osa(s1: &str, s2: &str) -> u32 {
    osa::distance(s1.chars(), s2.chars()) as u32
}

#[inline(always)]
fn osa_sim(s1: &str, s2: &str) -> f64 {
    osa::normalized_similarity(s1.chars(), s2.chars())
}

#[polars_expr(output_type=UInt32)]
fn pl_osa(inputs: &[Series], context: CallerContext) -> PolarsResult<Series> {
    let ca1 = inputs[0].str()?;
    let ca2 = inputs[1].str()?;
    let parallel = inputs[2].bool()?;
    let parallel = parallel.get(0).unwrap();
    let can_parallel = parallel && !context.parallel();
    if ca2.len() == 1 {
        let r = ca2.get(0).unwrap();
        let batched = osa::BatchComparator::new(r.chars());
        let out: UInt32Chunked = if can_parallel {
            POOL.install(|| {
                let n_threads = POOL.current_num_threads();
                let splits = split_offsets(ca1.len(), n_threads);
                let chunks: Vec<_> = splits
                    .into_par_iter()
                    .map(|(offset, len)| {
                        let s1 = ca1.slice(offset as i64, len);
                        let out: UInt32Chunked = s1
                            .apply_nonnull_values_generic(DataType::UInt32, |s| {
                                batched.distance(s.chars()) as u32
                            });
                        out.downcast_iter().cloned().collect::<Vec<_>>()
                    })
                    .collect();
                UInt32Chunked::from_chunk_iter(ca1.name(), chunks.into_iter().flatten())
            })
        } else {
            ca1.apply_nonnull_values_generic(DataType::UInt32, |s| {
                batched.distance(s.chars()) as u32
            })
        };
        Ok(out.into_series())
    } else if ca1.len() == ca2.len() {
        let out: UInt32Chunked = if can_parallel {
            POOL.install(|| {
                let n_threads = POOL.current_num_threads();
                let splits = split_offsets(ca1.len(), n_threads);
                let chunks: Vec<_> = splits
                    .into_par_iter()
                    .map(|(offset, len)| {
                        let s1 = ca1.slice(offset as i64, len);
                        let s2 = ca2.slice(offset as i64, len);
                        let out: UInt32Chunked = binary_elementwise_values(&s1, &s2, osa);
                        out.downcast_iter().cloned().collect::<Vec<_>>()
                    })
                    .collect();
                UInt32Chunked::from_chunk_iter(ca1.name(), chunks.into_iter().flatten())
            })
        } else {
            binary_elementwise_values(ca1, ca2, osa)
        };
        Ok(out.into_series())
    } else {
        Err(PolarsError::ShapeMismatch(
            "Inputs must have the same length or one of them must be a scalar.".into(),
        ))
    }
}

#[polars_expr(output_type=Float64)]
fn pl_osa_sim(inputs: &[Series], context: CallerContext) -> PolarsResult<Series> {
    let ca1 = inputs[0].str()?;
    let ca2 = inputs[1].str()?;
    let parallel = inputs[2].bool()?;
    let parallel = parallel.get(0).unwrap();
    let can_parallel = parallel && !context.parallel();
    if ca2.len() == 1 {
        let r = ca2.get(0).unwrap();
        let batched = osa::BatchComparator::new(r.chars());
        let out: Float64Chunked = if can_parallel {
            POOL.install(|| {
                let n_threads = POOL.current_num_threads();
                let splits = split_offsets(ca1.len(), n_threads);
                let chunks: Vec<_> = splits
                    .into_par_iter()
                    .map(|(offset, len)| {
                        let s1 = ca1.slice(offset as i64, len);
                        let out: Float64Chunked = s1
                            .apply_nonnull_values_generic(DataType::Float64, |s| {
                                batched.normalized_similarity(s.chars())
                            });
                        out.downcast_iter().cloned().collect::<Vec<_>>()
                    })
                    .collect();
                Float64Chunked::from_chunk_iter(ca1.name(), chunks.into_iter().flatten())
            })
        } else {
            ca1.apply_nonnull_values_generic(DataType::Float64, |s| {
                batched.normalized_similarity(s.chars())
            })
        };
        Ok(out.into_series())
    } else if ca1.len() == ca2.len() {
        let out: Float64Chunked = if can_parallel {
            POOL.install(|| {
                let n_threads = POOL.current_num_threads();
                let splits = split_offsets(ca1.len(), n_threads);
                let chunks: Vec<_> = splits
                    .into_par_iter()
                    .map(|(offset, len)| {
                        let s1 = ca1.slice(offset as i64, len);
                        let s2 = ca2.slice(offset as i64, len);
                        let out: Float64Chunked = binary_elementwise_values(&s1, &s2, osa_sim);
                        out.downcast_iter().cloned().collect::<Vec<_>>()
                    })
                    .collect();
                Float64Chunked::from_chunk_iter(ca1.name(), chunks.into_iter().flatten())
            })
        } else {
            binary_elementwise_values(ca1, ca2, osa_sim)
        };
        Ok(out.into_series())
    } else {
        Err(PolarsError::ShapeMismatch(
            "Inputs must have the same length or one of them must be a scalar.".into(),
        ))
    }
}
