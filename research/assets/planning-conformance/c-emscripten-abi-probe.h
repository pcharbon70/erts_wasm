#ifndef ERTS_WASM_C_EMSCRIPTEN_ABI_PROBE_H
#define ERTS_WASM_C_EMSCRIPTEN_ABI_PROBE_H

#include <stdint.h>

enum erts_wasm_probe_status {
    ERTS_WASM_PROBE_OK = 0,
    ERTS_WASM_PROBE_RANGE_ERROR = -1,
    ERTS_WASM_PROBE_STALE_GENERATION = -2,
    ERTS_WASM_PROBE_BUSY = -3,
    ERTS_WASM_PROBE_UNEXPECTED_COMPLETION = -4,
    ERTS_WASM_PROBE_HOST_ERROR = -5
};

uint32_t erts_wasm_probe_abi_version(void);
int32_t erts_wasm_probe_validate_slice(
    uint32_t offset, uint32_t length, uint32_t capacity);
void erts_wasm_probe_reset(uint32_t generation);
int32_t erts_wasm_probe_begin(
    uint32_t generation,
    uint32_t request_id,
    uint32_t offset,
    uint32_t length,
    uint32_t capacity);
int32_t erts_wasm_probe_complete(
    uint32_t generation, uint32_t request_id, int32_t status);

#endif
