import requests

def register_api_key(verification_secret, tenant_type, tenant_identifier, tenant_name, metadata=None):
    if metadata is None:
        metadata = {}

    registration_data = {
        'verification_secret': verification_secret,
        'tenant_type': tenant_type,
        'tenant_identifier': tenant_identifier,
        'tenant_name': tenant_name,
        'metadata': metadata
    }

    response = requests.post(
        'https://api.makeit3d.io/auth/register',
        headers={'Content-Type': 'application/json'},
        json=registration_data
    )

    if response.status_code != 200:
        raise Exception(f"Registration failed: {response.status_code} - {response.text}")

    return response.json()


if __name__ == "__main__":
    try:
        registration_response = register_api_key(
            verification_secret="n2K_KZX2PmFtF8Tn8_vDcqbP",  # 🔁 Replace with your secret
            tenant_type="shopify",  # or 'supabase_app'
            tenant_identifier="ai-image-app-dev-store.myshopify.com",  # 🔁 Replace with your shop domain
            tenant_name="Maxflow Image App",  # 🔁 Replace with your app name
            metadata={
                "app_version": "1.0.0",
                "developer": "Anas Rashid"
            }
        )

        print("✅ Registration successful!")
        print(f"API Key: {registration_response['api_key']}")
        print(f"Tenant ID: {registration_response['tenant_id']}")
        print(f"Tenant Type: {registration_response['tenant_type']}")

    except Exception as e:
        print(f"❌ Registration failed: {e}")
