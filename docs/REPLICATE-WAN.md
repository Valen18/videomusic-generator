

export REPLICATE_API_TOKEN=r8_TlGTFBBsFkqhh8x8Kyk1vsDNVxY78Ha3GYih8



Run wan-video/wan-2.2-i2v-fast using Replicate’s API. Check out the model's schema for an overview of inputs and outputs.

curl --silent --show-error https://api.replicate.com/v1/models/wan-video/wan-2.2-i2v-fast/predictions \
	--request POST \
	--header "Authorization: Bearer $REPLICATE_API_TOKEN" \
	--header "Content-Type: application/json" \
	--header "Prefer: wait" \
	--data @- <<'EOM'
{
	"input": {
      "image": "https://replicate.delivery/pbxt/NRvtedaIOd3pdE0pTE3L9uavxJ53g33THGr0HF81M2olNOce/replicate-prediction-g8gbs3rbk9rme0crbhwatpsq04.jpg",
      "prompt": "Close-up shot of an elderly sailor wearing a yellow raincoat, seated on the deck of a catamaran, slowly puffing on a pipe. His cat lies quietly beside him with eyes closed, enjoying the calm. The warm glow of the setting sun bathes the scene, with gentle waves lapping against the hull and a few seabirds circling slowly above. The camera slowly pushes in, capturing this peaceful and harmonious moment."
	}
}
EOM