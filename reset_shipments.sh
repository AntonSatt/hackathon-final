#!/bin/bash
# Reset shipments.json to clean state (empty)
# ./reset_shipments.sh

cat > shipments.json << 'EOF'
{}
EOF

echo "✅ shipments.json has been reset to clean state (empty)"
