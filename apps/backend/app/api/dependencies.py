import os
from supabase import create_client, Client
from app.services.supabase_service import SupabaseService
from fastapi import Request

# Usually fetched from environment variables
SUPABASE_URL = os.environ.get("SUPABASE_URL", "http://localhost:8000") # placeholder
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "placeholder_key")

# We can cache the client
_supabase_client = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_client

def get_supabase_service() -> SupabaseService:
    client = get_supabase_client()
    return SupabaseService(client)
