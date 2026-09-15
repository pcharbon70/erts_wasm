#include "c-emscripten-abi-probe.h"

#include <stdint.h>

static uint32_t submit_count;
static uint32_t wake_count;

int32_t erts_wasm_host_submit(
    uint32_t generation,
    uint32_t request_id,
    uint32_t offset,
    uint32_t length)
{
    (void)generation;
    (void)request_id;
    (void)offset;
    (void)length;
    submit_count += 1;
    return ERTS_WASM_PROBE_OK;
}

void erts_wasm_host_wake(uint32_t generation)
{
    (void)generation;
    wake_count += 1;
}

#define CHECK(expression) do { if (!(expression)) return __LINE__; } while (0)

int main(void)
{
    CHECK(erts_wasm_probe_abi_version() == UINT32_C(1));
    CHECK(erts_wasm_probe_validate_slice(0, 0, 0) == ERTS_WASM_PROBE_OK);
    CHECK(erts_wasm_probe_validate_slice(0, 1, 0) == ERTS_WASM_PROBE_RANGE_ERROR);
    CHECK(
        erts_wasm_probe_validate_slice(UINT32_MAX, 1, UINT32_MAX) ==
        ERTS_WASM_PROBE_RANGE_ERROR);

    erts_wasm_probe_reset(UINT32_C(7));
    CHECK(
        erts_wasm_probe_begin(6, 41, 0, 0, 0) ==
        ERTS_WASM_PROBE_STALE_GENERATION);
    CHECK(erts_wasm_probe_begin(7, 42, 8, 4, 12) == ERTS_WASM_PROBE_OK);
    CHECK(submit_count == 1);
    CHECK(erts_wasm_probe_begin(7, 43, 0, 0, 0) == ERTS_WASM_PROBE_BUSY);
    CHECK(
        erts_wasm_probe_complete(7, 43, ERTS_WASM_PROBE_OK) ==
        ERTS_WASM_PROBE_UNEXPECTED_COMPLETION);
    CHECK(
        erts_wasm_probe_complete(7, 42, ERTS_WASM_PROBE_OK) ==
        ERTS_WASM_PROBE_OK);
    CHECK(wake_count == 1);
    CHECK(
        erts_wasm_probe_complete(7, 42, ERTS_WASM_PROBE_OK) ==
        ERTS_WASM_PROBE_UNEXPECTED_COMPLETION);
    return 0;
}
