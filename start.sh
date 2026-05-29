#!/bin/bash
source /run/media/deck/1d979ec9-f997-465f-9d38-8b32835ce1bf/miniconda3/etc/profile.d/conda.sh
conda activate scorecard
cd ~/supplier-scorecard
flatpak run com.visualstudio.code . &
sleep 3
echo "✅ VS Code gestartet – Umgebung: scorecard"
read -p "Alt+F4 drücken zum Schließen..."
