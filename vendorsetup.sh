mkdir -p "prebuilts/clang/host/linux-x86/neutron-clang"
cd "prebuilts/clang/host/linux-x86/neutron-clang"
curl -LO "https://raw.githubusercontent.com/Neutron-Toolchains/antman/main/antman"
chmod +x antman
./antman -S
cd ~/evolution
