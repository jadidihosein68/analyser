class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mssql+pyodbc:///?"
        "Driver=%7BODBC+Driver+17+for+SQL+Server%7D;"
        "Server=DESKTOP-BV0EM2G;"
        "Database=traider;"
        "Trusted_Connection=yes;"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SCHEDULER_API_ENABLED = True
