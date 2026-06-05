mkdir -p "prebuilts/clang/host/linux-x86/clang-neutron"
cd "prebuilts/clang/host/linux-x86/clang-neutron"
curl -LO "https://raw.githubusercontent.com/Neutron-Toolchains/antman/main/antman"
chmod +x antman
./antman -S
cd ~/evolution
