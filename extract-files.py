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
        'libPanelChaplin',
        'libhwconfigurationutil',
        'vendor.oplus.hardware.camera_rfi-V3-ndk',
        'vendor.oplus.hardware.cammidasservice-V1-ndk',
        'vendor.oplus.hardware.displaycolorfeature-V1-ndk',
    ): lib_fixup_vendor_suffix,
}

blob_fixups: blob_fixups_user_type = {
    'odm/etc/camera/CameraHWConfiguration.config': blob_fixup()
        # Disable face detection AE behaviour
        .regex_replace(r'(enableSWfdForThirdCamUnit += )TRUE', r'\1FALSE')
        .regex_replace(r'(fdSupport += )TRUE;', r'\1FALSE;')
        # Expose AUX cameras
        .regex_replace('SystemCamera =  0;  0;  0;  1;  0; 1;', 'SystemCamera =  0;  0;  0;  0;  0; 0;'),
    (
        'odm/etc/libnfc-mtp-SN220.conf_24831',
        'odm/etc/libnfc-mtp-SN220.conf_24863'
    ): blob_fixup()
        .regex_replace('(NXPLOG_.*_LOGLEVEL)=0x03', '\\1=0x02')
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
    ('odm/lib64/libEIS.so', 'odm/lib64/libEISLive.so', 'odm/lib64/libOPAlgoCamFaceBeautyCap.so'): blob_fixup()
        .clear_symbol_version('AHardwareBuffer_allocate')
        .clear_symbol_version('AHardwareBuffer_describe')
        .clear_symbol_version('AHardwareBuffer_lock')
        .clear_symbol_version('AHardwareBuffer_release')
        .clear_symbol_version('AHardwareBuffer_unlock'),
    'vendor/etc/libnfc-nci.conf': blob_fixup()
        .regex_replace('NFC_DEBUG_ENABLED=1', 'NFC_DEBUG_ENABLED=0'),
}  # fmt: skip

module = ExtractUtilsModule(
    'infiniti',
    'oneplus',
    namespace_imports=namespace_imports,
    blob_fixups=blob_fixups,
    lib_fixups=lib_fixups,
#    add_firmware_proprietary_file=True,
)

if __name__ == '__main__':
    utils = ExtractUtils.device_with_common(
        module, 'sm8850-common', module.vendor
    )
    utils.run()
