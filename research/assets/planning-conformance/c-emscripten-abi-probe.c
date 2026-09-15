#include "c-emscripten-abi-probe.h"

#include <limits.h>
#include <stdint.h>

#if defined(__EMSCRIPTEN__)
#include <emscripten/emscripten.h>
#define ERTS_WASM_EXPORT EMSCRIPTEN_KEEPALIVE
#else
#define ERTS_WASM_EXPORT
#endif

_Static_assert(CHAR_BIT == 8, "the probe requires eight-bit bytes");
_Static_assert(sizeof(uint32_t) == 4, "uint32_t must be 32 bits");
_Static_assert(sizeof(int32_t) == 4, "int32_t must be 32 bits");
#if defined(__EMSCRIPTEN__)
_Static_assert(sizeof(uintptr_t) == 4, "the selected Wasm target is wasm32");
#endif

extern int32_t erts_wasm_host_submit(
    uint32_t generation,
    uint32_t request_id,
    uint32_t offset,
    uint32_t length);
extern void erts_wasm_host_wake(uint32_t generation);

static uint32_t active_generation;
static uint32_t pending_request;
static int request_pending;

ERTS_WASM_EXPORT uint32_t erts_wasm_probe_abi_version(void)
{
    return UINT32_C(1);
}

ERTS_WASM_EXPORT int32_t erts_wasm_probe_validate_slice(
    uint32_t offset, uint32_t length, uint32_t capacity)
{
    if (offset > capacity || length > capacity - offset) {
        return ERTS_WASM_PROBE_RANGE_ERROR;
    }
    return ERTS_WASM_PROBE_OK;
}

ERTS_WASM_EXPORT void erts_wasm_probe_reset(uint32_t generation)
{
    active_generation = generation;
    pending_request = 0;
    request_pending = 0;
}

ERTS_WASM_EXPORT int32_t erts_wasm_probe_begin(
    uint32_t generation,
    uint32_t request_id,
    uint32_t offset,
    uint32_t length,
    uint32_t capacity)
{
    int32_t result;

    if (generation != active_generation) {
        return ERTS_WASM_PROBE_STALE_GENERATION;
    }
    result = erts_wasm_probe_validate_slice(offset, length, capacity);
    if (result != ERTS_WASM_PROBE_OK) {
        return result;
    }
    if (request_pending) {
        return ERTS_WASM_PROBE_BUSY;
    }

    pending_request = request_id;
    request_pending = 1;
    result = erts_wasm_host_submit(generation, request_id, offset, length);
    if (result != ERTS_WASM_PROBE_OK) {
        pending_request = 0;
        request_pending = 0;
        return ERTS_WASM_PROBE_HOST_ERROR;
    }
    return ERTS_WASM_PROBE_OK;
}

ERTS_WASM_EXPORT int32_t erts_wasm_probe_complete(
    uint32_t generation, uint32_t request_id, int32_t status)
{
    if (generation != active_generation) {
        return ERTS_WASM_PROBE_STALE_GENERATION;
    }
    if (!request_pending || request_id != pending_request) {
        return ERTS_WASM_PROBE_UNEXPECTED_COMPLETION;
    }

    pending_request = 0;
    request_pending = 0;
    erts_wasm_host_wake(generation);
    return status;
}
