from languru.server.build_llm_app import create_app, run_app

app = create_app()


if __name__ == "__main__":
    run_app(app)
