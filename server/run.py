import uvicorn


if __name__ == "__main__":
    # uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)