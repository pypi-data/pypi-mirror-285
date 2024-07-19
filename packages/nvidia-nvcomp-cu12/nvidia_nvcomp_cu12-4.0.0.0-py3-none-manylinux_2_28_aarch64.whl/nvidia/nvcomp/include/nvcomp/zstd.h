/*
 * SPDX-FileCopyrightText: Copyright (c) 2022-2024 NVIDIA CORPORATION & AFFILIATES.
 * All rights reserved. SPDX-License-Identifier: LicenseRef-NvidiaProprietary
 *
 * NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
 * property and proprietary rights in and to this material, related
 * documentation and any modifications thereto. Any use, reproduction,
 * disclosure or distribution of this material and related documentation
 * without an express license agreement from NVIDIA CORPORATION or
 * its affiliates is strictly prohibited.
*/

#ifndef NVCOMP_Zstd_H
#define NVCOMP_Zstd_H

#include "nvcomp.h"

#include <cuda_runtime.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/******************************************************************************
 * Batched compression/decompression interface for Zstd
 *****************************************************************************/

/**
 * @brief Zstd compression options for the low-level API
 */
typedef struct
{
  int reserved;
} nvcompBatchedZstdOpts_t;

static const nvcompBatchedZstdOpts_t nvcompBatchedZstdDefaultOpts = {0};

// To go higher than 1 << 31 - 1, would require 64-bit math in a number of places
const size_t nvcompZstdCompressionMaxAllowedChunkSize = (1UL << 31) - 1;

/**
 * This is the minimum alignment required for void type CUDA memory buffers
 * passed to compression or decompression functions.  Typed memory buffers must
 * still be aligned to their type's size, e.g. 8 bytes for size_t.
 */
const size_t nvcompZstdRequiredAlignment = 8;

/**
 * @brief Get the amount of temporary memory required on the GPU for compression.
 *
 * Chunk size must not exceed 16 MB.
 * For best performance, a chunk size of 64 KB is recommended.
 *
 * @param[in] num_chunks The number of chunks of memory in the batch.
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk in the
 * batch.
 * @param[in] format_opts The ZSTD compression options to use -- currently empty
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily
 * required during compression.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdCompressGetTempSize(
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedZstdOpts_t format_opts,
    size_t* temp_bytes);

/**
 * @brief Get the amount of temporary memory required on the GPU for compression
 * with extra total bytes argument.
 *
 * Chunk size must not exceed 16 MB.
 * For best performance, a chunk size of 64 KB is recommended.
 *
 * This extended API is useful for cases where chunk sizes aren't uniform in the batch
 * I.e. in the non-extended API, if all but 1 chunk is 64 KB, but 1 chunk is
 * 16 MB, the temporary space computed is based on 16 MB * num_chunks.
 *
 * @param[in] num_chunks The number of chunks of memory in the batch.
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk in the
 * batch.
 * @param[in] format_opts The ZSTD compression options to use. Currently empty.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily
 * required during compression.
 * @param[in] max_total_uncompressed_bytes Upper bound on the total uncompressed
 * size of all chunks
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdCompressGetTempSizeEx(
    size_t num_chunks,
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedZstdOpts_t format_opts,
    size_t* temp_bytes,
    const size_t max_total_uncompressed_bytes);

/**
 * @brief Get the maximum size that a chunk of size at most max_uncompressed_chunk_bytes
 * could compress to. That is, the minimum amount of output memory required to be given
 * nvcompBatchedZstdCompressAsync() for each chunk.
 *
 * Chunk size must not exceed 16 MB.
 * For best performance, a chunk size of 64 KB is recommended.
 *
 * @param[in] max_uncompressed_chunk_bytes The maximum size of a chunk before compression.
 * @param[in] format_opts The Zstd compression options to use. Currently empty.
 * @param[out] max_compressed_chunk_bytes The maximum possible compressed size of the chunk.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdCompressGetMaxOutputChunkSize(
    size_t max_uncompressed_chunk_bytes,
    nvcompBatchedZstdOpts_t format_opts,
    size_t* max_compressed_chunk_bytes);

/**
 * @brief Perform batched asynchronous compression.
 *
 * The individual chunk size must not exceed 16 MB.
 * For best performance, a chunk size of 64 KB is recommended.
 *
 * @param[in] device_uncompressed_chunk_ptrs Array with size \p num_chunks of pointers
 * to the uncompressed data chunks. Both the pointers and the uncompressed data
 * should reside in device-accessible memory.
 * @param[in] device_uncompressed_chunk_bytes Array with size \p num_chunks of
 * sizes of the uncompressed chunks in bytes.
 * The sizes should reside in device-accessible memory.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest uncompressed chunk.
 * This parameter is currently unused, so if it is not set
 * with the maximum size, it should be set to zero. If a future version makes
 * use of it, it will return an error if it is set to zero.
 * @param[in] num_chunks Number of chunks of data to compress.
 * @param[in] device_temp_ptr The temporary GPU workspace, could be NULL in case
 * temporary memory is not needed.
 * @param[in] temp_bytes The size of the temporary GPU memory pointed to by
 * `device_temp_ptr`.
 * @param[out] device_compressed_chunk_ptrs Array with size \p num_chunks of pointers
 * to the output compressed buffers. Both the pointers and the compressed
 * buffers should reside in device-accessible memory. Each compressed buffer
 * should be preallocated with the size given by
 * `nvcompBatchedZstdCompressGetMaxOutputChunkSize`.
 * @param[out] device_compressed_chunk_bytes Array with size \p num_chunks, 
 * to be filled with the compressed sizes of each chunk.
 * The buffer should be preallocated in device-accessible memory.
 * @param[in] format_opts The Zstd compression options to use. Currently empty.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successfully launched, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdCompressAsync(
    const void* const* device_uncompressed_chunk_ptrs,
    const size_t* device_uncompressed_chunk_bytes,
    size_t max_uncompressed_chunk_bytes,
    size_t num_chunks,
    void* device_temp_ptr,
    size_t temp_bytes,
    void* const* device_compressed_chunk_ptrs,
    size_t* device_compressed_chunk_bytes,
    nvcompBatchedZstdOpts_t format_opts,
    cudaStream_t stream);

/**
 * @brief Get the amount of temporary memory required on the GPU for decompression.
 *
 * @param[in] num_chunks Number of chunks of data to be decompressed.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest chunk in bytes
 * when uncompressed.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily required
 * during decompression.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdDecompressGetTempSize(
    size_t num_chunks, size_t max_uncompressed_chunk_bytes, size_t* temp_bytes);

/**
 * @brief Get the amount of temporary memory required on the GPU for decompression
 * with extra total bytes argument.
 *
 * @param[in] num_chunks Number of chunks of data to be decompressed.
 * @param[in] max_uncompressed_chunk_bytes The size of the largest chunk in bytes
 * when uncompressed.
 * @param[out] temp_bytes The amount of GPU memory that will be temporarily required
 * during decompression.
 * @param[in] max_total_uncompressed_bytes  The total decompressed size of all the chunks. 
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdDecompressGetTempSizeEx(
    size_t num_chunks, size_t max_uncompressed_chunk_bytes,
    size_t* temp_bytes, size_t max_total_uncompressed_bytes);

/**
 * @brief Asynchronously compute the number of bytes of uncompressed data for
 * each compressed chunk.
 *
 * @param[in] device_compressed_chunk_ptrs Array with size \p num_chunks of
 * pointers in device-accessible memory to compressed buffers.
 * @param[in] device_compressed_chunk_bytes Array with size \p num_chunks of sizes
 * of the compressed buffers in bytes. The sizes should reside in device-accessible memory.
 * @param[out] device_uncompressed_chunk_bytes Array with size \p num_chunks
 * to be filled with the sizes, in bytes, of each uncompressed data chunk.
 * If there is an error when retrieving the size of a chunk, the
 * uncompressed size of that chunk will be set to 0. This argument needs to
 * be prealloated in device-accessible memory.
 * @param[in] num_chunks Number of data chunks to compute sizes of.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successful, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdGetDecompressSizeAsync(
    const void* const* device_compressed_chunk_ptrs,
    const size_t* device_compressed_chunk_bytes,
    size_t* device_uncompressed_chunk_bytes,
    size_t num_chunks,
    cudaStream_t stream);

/**
 * @brief Perform batched asynchronous decompression.
 *
 * @param[in] device_compressed_chunk_ptrs Array with size \p num_chunks of pointers
 * in device-accessible memory to compressed buffers. Each compressed buffer
 * should reside in device-accessible memory.
 * @param[in] device_compressed_chunk_bytes Array with size \p num_chunks of sizes of
 * the compressed buffers in bytes. The sizes should reside in device-accessible memory.
 * @param[in] device_uncompressed_buffer_bytes Array with size \p num_chunks of sizes,
 * in bytes, of the output buffers to be filled with uncompressed data for each chunk.
 * The sizes should reside in device-accessible memory. If a
 * size is not large enough to hold all decompressed data, the decompressor
 * will set the status in \p device_statuses corresponding to the
 * overflow chunk to `nvcompErrorCannotDecompress`.
 * @param[out] device_uncompressed_chunk_bytes Array with size \p num_chunks to
 * be filled with the actual number of bytes decompressed for every chunk.
 * @param[in] num_chunks Number of chunks of data to decompress.
 * @param[in] device_temp_ptr The temporary GPU space, could be NULL in case temporary space is not needed.
 * @param[in] temp_bytes The size of the temporary GPU space.
 * @param[out] device_uncompressed_chunk_ptrs Array with size \p num_chunks of
 * pointers in device-accessible memory to decompressed data. Each uncompressed
 * buffer needs to be preallocated in device-accessible memory, have the size
 * specified by the corresponding entry in device_uncompressed_buffer_bytes.
 * @param[out] device_statuses Array with size \p num_chunks of statuses in
 * device-accessible memory. This argument needs to be preallocated. For each
 * chunk, if the decompression is successful, the status will be set to
 * `nvcompSuccess`. If the decompression is not successful, for example due to
 * the corrupted input or out-of-bound errors, the status will be set to
 * `nvcompErrorCannotDecompress`.
 * @param[in] stream The CUDA stream to operate on.
 *
 * @return nvcompSuccess if successfully launched, and an error code otherwise.
 */
NVCOMP_EXPORT
nvcompStatus_t nvcompBatchedZstdDecompressAsync(
    const void* const* device_compressed_chunk_ptrs,
    const size_t* device_compressed_chunk_bytes,
    const size_t* device_uncompressed_buffer_bytes,
    size_t* device_uncompressed_chunk_bytes,
    size_t num_chunks,
    void* const device_temp_ptr,
    size_t temp_bytes,
    void* const* device_uncompressed_chunk_ptrs,
    nvcompStatus_t* device_statuses,
    cudaStream_t stream);

#ifdef __cplusplus
}
#endif

#endif
