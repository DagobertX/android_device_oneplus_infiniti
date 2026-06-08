#!/usr/bin/env -S PYTHONPATH=../../../tools/extract-utils python3
#
# SPDX-FileCopyrightText: 2024 The LineageOS Project
# SPDX-License-Identifier: Apache-2.0
#

from extract_utils.fixups_blob import (
    blob_fixup,
    blob_fixups_user_type,
)
from extract_utils.fixups_lib import (
    lib_fixups,
    lib_fixups_user_type,
)
from extract_utils.main import (
    ExtractUtils,
    ExtractUtilsModule,
)

namespace_imports = [
    'hardware/oplus',
    'hardware/qcom-caf/sm8850',
    'vendor/oneplus/sm8850-common',
    'vendor/qcom/opensource/commonsys-intf/display',
]


def lib_fixup_vendor_suffix(lib: str, partition: str, *args, **kwargs):
    return f'{lib}_{partition}' if partition == 'vendor' else None


lib_fixups: lib_fixups_user_type = {
    **lib_fixups,
    (
        'libhcsutils',
        'vendor.oplus.hardware.camera.aon-V1-ndk',
        'vendor.oplus.hardware.camera_rfi-V3-ndk',
        'vendor.oplus.hardware.cammidasservice-V1-ndk',
        'vendor.oplus.hardware.sendextcamcmd-V2-ndk',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    # NOTE (2026-06-08): the org baseline (waffle a56e075 "Disable face detection
    # AE behavior") forced fdSupport / enableSWfdForThirdCamUnit TRUE -> FALSE.
    # That overrides the OOS value (both TRUE in stock CameraHWConfiguration.config)
    # and breaks the PC4/CoupleHDR SW face-detect plumbing the OplusCamera capture
    # path relies on. Restore the OOS baseline by NOT rewriting these keys
    # (facilitate, do not force).
    'odm/etc/init/init.camera_process.rc': blob_fixup()
        .regex_replace('    delete_recursion', '    #delete_recursion'),
    (
        'odm/etc/libnfc-mtp-SN220.conf_24831',
        'odm/etc/libnfc-mtp-SN220.conf_24863',
    ): blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    (
        'odm/lib64/libAlgoProcess.so',
        'odm/lib64/libEIS.so',
        'odm/lib64/libEISLive.so',
        'odm/lib64/libFaceBeautyJni.so',
        'odm/lib64/libFaceDistortionCorrection.so',
        'odm/lib64/libOPAlgoCamAiBeautyFaceRetouchCn.so',
        'odm/lib64/libOPAlgoCamAiUnifySkin.so',
        'odm/lib64/libOPAlgoCamFaceBeautyCap.so',
        'odm/lib64/libaiboost_te.so',
    ): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_acquire')
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_lockPlanes')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    'odm/lib64/libAlgoProcess.so': blob_fixup()
        .replace_needed('android.hardware.graphics.common-V5-ndk.so', 'android.hardware.graphics.common-V7-ndk.so')
        # P010 plane-layout fix at RUNTIME by libapsfixup.so (built from
        # vendor/oplus/camera-sm8850/apsfixup), loaded via this DT_NEEDED. Root cause: the
        # port's gralloc returns a non-contiguous P010 plane layout (A16 Gralloc5
        # AHardwareBuffer_lockPlanes per-plane VAs) to the byte-identical ArcSoft/Algo blobs,
        # so they build a garbage chroma plane ptr (was align_up(luma,0)), a zero chroma
        # pitch, and a garbage p010 conversion length -> ~1 GB walk off a 36 MB dmabuf ->
        # SIGSEGV. The interposer corrects all three at runtime via GOT/PLT JUMP_SLOT redirect
        # (no code patch, no execmem); no-op on correct buffers. See docs/rearch/19,20 +
        # vendor/oplus/camera-sm8850/apsfixup/docs/PORTING.md. The binary
        # min()/described-height geometry patch on this blob STAYS as the proven fallback
        # until libapsfixup is device-validated (apsfixup/docs/frida/op_chroma_repair.js),
        # then drop it.
        .add_needed('libapsfixup.so'),
    'odm/lib64/liboprec_audrec.so': blob_fixup()
        .replace_needed('libstdc++.so', 'libstdc++_vendor.so'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    # NOTE (2026-06-08, worker-1, docs/rearch/14): KEEP this V1->V2 relink — it is
    # a pure LOADABILITY fixup, NOT a behavior change. Both blobs carry a *vestigial*
    # DT_NEEDED on allocator-V1-ndk (over-linked at build time) but import ZERO graphics
    # allocator AIDL symbols (`nm -D -u` => only std::allocator<char> + allocate_camera_metadata).
    # V1's exported symbol set is a strict SUBSET of V2 (43 ⊂ 54), and the libs that
    # actually drive allocation (libui.so, mapper.qti.so) NEED only V2 — on OOS too.
    # The real alloc path (libui -> mapper.qti.so -> display.allocator-service) is V2 on
    # BOTH OOS and LOS with byte-identical gralloc binaries. => Providing the OOS
    # allocator-V1-ndk.so on LOS would change NOTHING about P010 plane contiguity; the
    # V1-allocator contiguity hypothesis is REFUTED. Do NOT drop this relink and do NOT
    # ship V1 (would add a dead blob). The non-contiguity divergence is consumer-side
    # (libAlgoProcess lockPlanes / graphics.common ABI), not in the allocation plumbing.
    (
        'vendor/lib64/camera/components/com.qti.node.dewarp.so',
        'vendor/lib64/vendor.qti.hardware.camera.offlinecamera-service-impl.so',
    ): blob_fixup()
        .replace_needed('android.hardware.graphics.allocator-V1-ndk.so', 'android.hardware.graphics.allocator-V2-ndk.so'),
    (
        'vendor/lib64/camera/components/com.qti.node.fd.so',
        'vendor/lib64/hw/camera.qcom.core.so',
        'vendor/lib64/libcamxdumpinforecorder.so',
    ): blob_fixup()
        .replace_needed('libtinyxml2.so', 'libtinyxml2-v36.so'),
}  # fmt: skip

module = ExtractUtilsModule(
    'infiniti',
    'oneplus',
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
    namespace_imports=namespace_imports,
    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8850-common', module.vendor
    )
    utils.run()
