# brainDoc

This project is a web-based application built with **Django**, **HTML**, **CSS**, and **JavaScript**, along with **Phidata** as the framework. It allows users to upload PDF files, interact with them through a chat-like interface, and retrieve previous interactions for review. It supports multiple PDF uploads and remembers all previous chats.

## Features

- **User Authentication**:
  - Login with email and password.
  - Google login for faster access.

- **PDF Upload and Interaction**:
  - Upload single or multiple PDF files.
  - Interact with PDFs via an intuitive chat interface.
  - Engage in meaningful dialogue related to the uploaded PDFs.

- **Chat Memory**:
  - System remembers all previous interactions, allowing users to pick up where they left off.
  - Retrieve and review all past conversations related to uploaded PDFs.

- **Multiple PDF Support**:
  - Upload and interact with more than one PDF simultaneously.
  - Keep track of all chats corresponding to different PDF files.

## Installation and Setup

### Prerequisites

- Python 3.7+
- Django 4.0+
- Phidata (for framework setup)
- A Google OAuth 2.0 client setup (for Google login functionality)



## Usage

1. **Login/Register** using the standard email/password option or through Google OAuth.
2. **Upload PDFs** by selecting them from your device.
3. **Interact** with the uploaded PDFs through a chat interface, where the system responds based on the content of the file.
4. **Retrieve Previous Chats** to view or continue interactions.
5. **Upload and Manage Multiple PDFs** for simultaneous engagement and interaction.

## Technologies Used

- **Backend**: Django, Phidata
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Custom authentication + Google OAuth 2.0
- **File Management**: PDF handling and multiple file upload support

## Contributing

1. Fork the repository.
2. Create a new feature branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m 'Add a feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Here’s the "Installation and Setup" section for your README:

---

## Installation and Setup

### Prerequisites

- Python 3.7+
- Django 4.0+
- Phidata (for framework setup)
- A Google OAuth 2.0 client setup (for Google login functionality)

### Instructions

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Pneumotional/brainDoc.git
   cd brainDoc
   ```

2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Google OAuth**:

   - Set up your Google OAuth credentials on the [Google Developer Console](https://console.cloud.google.com/).
   - Download the OAuth client credentials file and add it to your project.
   - Update the `settings.py` file with your OAuth credentials.

5. **Run Migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

7. **Access the application**:

   Open your browser and go to:

   ```
   http://127.0.0.1:8000
   ```

---

## Credentials
username: admin
pass: admin

