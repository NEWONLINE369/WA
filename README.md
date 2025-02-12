# WhatsApp Automation Tool 📱

A multi-user WhatsApp message automation platform built with Streamlit, enabling bulk messaging through CSV/Excel file uploads.

## Features

- 👥 Multi-user support with authentication
- 📊 Bulk message sending via CSV/Excel upload
- 🔒 Secure credential management per user
- 📝 Message status tracking
- ⏱️ Customizable message delay
- 📎 Support for attachments

## Prerequisites

- Python 3.11+
- PostgreSQL database
- WhatsApp API credentials (instance ID and access token)

## Environment Variables

The following environment variables are required:

```env
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/[your-username]/whatsapp-automation-tool.git
cd whatsapp-automation-tool
```

2. Install dependencies:
```bash
pip install streamlit pandas openpyxl requests sqlalchemy bcrypt psycopg2-binary
```

3. Set up the database:
- Ensure PostgreSQL is running
- Set the DATABASE_URL environment variable
- The application will automatically create the necessary tables on first run

4. Run the application:
```bash
streamlit run main.py
```

## CSV/Excel File Format

Your input file should have the following columns:
- Mobile Number
- Name
- Message
- Attachment (URL link)
- Time (delay in minutes)

## Security Features

- Password hashing using bcrypt
- Secure credential storage
- SSL-enabled database connections
- Session management

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
