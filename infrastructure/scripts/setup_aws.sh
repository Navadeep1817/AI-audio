#!/bin/bash

set -e

BUCKET_NAME="ai-sales-coach-audio"
REGION="us-east-1"

# Use local temp files (cross-platform safe)
TMP_CORS_FILE="cors.json"
TMP_LIFECYCLE_FILE="lifecycle.json"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  S3 BUCKET SETUP FOR AI SALES COACH"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── Step 1: Create bucket ─────────────────────────────────────────────
echo "→ Creating S3 bucket: ${BUCKET_NAME} in ${REGION}..."

if aws s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo "  ✓ Bucket already exists"
else
  aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$REGION"
  echo "  ✓ Bucket created"
fi

# ── Step 2: Enable versioning ────────────────────────────────────────
echo ""
echo "→ Enabling versioning..."
aws s3api put-bucket-versioning \
  --bucket "$BUCKET_NAME" \
  --versioning-configuration Status=Enabled
echo "  ✓ Versioning enabled"

# ── Step 3: Configure CORS ───────────────────────────────────────────
echo ""
echo "→ Configuring CORS..."

cat > "$TMP_CORS_FILE" <<'EOF'
{
  "CORSRules": [
    {
      "AllowedOrigins": ["http://localhost:5173", "http://localhost:3000"],
      "AllowedMethods": ["PUT", "POST", "GET"],
      "AllowedHeaders": ["*"],
      "MaxAgeSeconds": 3000
    }
  ]
}
EOF

aws s3api put-bucket-cors \
  --bucket "$BUCKET_NAME" \
  --cors-configuration file://$TMP_CORS_FILE

echo "  ✓ CORS configured"

# ── Step 4: Lifecycle policy ─────────────────────────────────────────
echo ""
echo "→ Configuring lifecycle policy..."

cat > "$TMP_LIFECYCLE_FILE" <<'EOF'
{
  "Rules": [
    {
      "ID": "DeleteOldAudio",
      "Status": "Enabled",
      "Prefix": "audio-uploads/",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket "$BUCKET_NAME" \
  --lifecycle-configuration file://$TMP_LIFECYCLE_FILE

echo "  ✓ Lifecycle policy set"

# ── Step 5: Block public access ──────────────────────────────────────
echo ""
echo "→ Blocking public access..."
aws s3api put-public-access-block \
  --bucket "$BUCKET_NAME" \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "  ✓ Public access blocked"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✓ S3 bucket setup complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
