# Patch for external_oauth_source_configs.py
# Add Facebook OAuth Provider Configuration

# Location: flexus/flexus_backend/flexus_v1/external_oauth_source_configs.py
# Insert after LinkedIn configuration (around line 196)

"facebook": OAuthProviderConfig(
    oap_provider_key="facebook",
    oap_display_name="Facebook",
    oap_service_provider="facebook",
    oap_client_id_env="FACEBOOK_CLIENT_ID",
    oap_client_secret_env="FACEBOOK_CLIENT_SECRET",
    oap_authorize_url="https://www.facebook.com/v19.0/dialog/oauth",
    oap_token_url="https://graph.facebook.com/v19.0/oauth/access_token",
    oap_scope="ads_management,ads_read,read_insights",
    oap_redirect_path="/v1/tool-oauth/facebook/callback",
    oap_token_request_auth="body",  # Facebook uses body, not basic auth
    oap_post_auth_redirect_path="/profile",
    oap_auth_type="oauth2",
    oap_extra_token_params={},
    oap_token_request_headers={},
    oap_supports_refresh=True,
    oap_minimum_expiry_margin=120,
    oap_scope_delimiter=",",  # Facebook uses comma, not space
    oap_extra_authorize_params={
        "auth_type": "rerequest",  # Re-request declined permissions
    },
    oap_available_scopes=(
        HumanReadableScope("ads_management", "Create and manage ads"),
        HumanReadableScope("ads_read", "Read ads data"),
        HumanReadableScope("read_insights", "Access ads analytics"),
        HumanReadableScope("business_management", "Manage Business Manager accounts"),
        HumanReadableScope("pages_show_list", "Read list of Pages managed by a person"),
        HumanReadableScope("pages_read_engagement", "Read engagement data for Pages"),
        HumanReadableScope("pages_manage_ads", "Create and manage ads for Pages"),
        HumanReadableScope("pages_read_user_content", "Read user-generated content on Pages"),
        HumanReadableScope("instagram_basic", "Access Instagram basic data"),
        HumanReadableScope("instagram_manage_insights", "Access Instagram insights"),
    ),
),


