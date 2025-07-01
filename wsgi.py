from app import app

# This file is necessary for Vercel deployment
app.config['DEBUG'] = True

if __name__ == "__main__":
    app.run()
