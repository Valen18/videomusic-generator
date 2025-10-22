export REPLICATE_API_TOKEN=r8_TlGTFBBsFkqhh8x8Kyk1vsDNVxY78Ha3GYih8


Run bytedance/seedream-4 using Replicate’s API. Check out the model's schema for an overview of inputs and outputs.

curl --silent --show-error https://api.replicate.com/v1/models/bytedance/seedream-4/predictions \
	--request POST \
	--header "Authorization: Bearer $REPLICATE_API_TOKEN" \
	--header "Content-Type: application/json" \
	--header "Prefer: wait" \
	--data @- <<'EOM'
{
	"input": {
      "prompt": "a photo of a store front called \"Seedream 4\", it sells books, a poster in the window says \"Seedream 4 now on Replicate\"",
      "aspect_ratio": "4:3"
	}
}
EOM
