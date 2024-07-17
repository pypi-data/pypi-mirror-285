import os

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 3000))
    uvicorn.run("cbr_website_beta.fast_api_main:app", host="0.0.0.0", port=port, reload=True)