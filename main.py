import streamlit as st
import pandas as pd
import time
from whatsapp_sender import WhatsAppSender
from data_processor import DataProcessor
from models import get_db, User # Added import for database models
from auth import init_session_state, create_user, authenticate_user, login_user, logout_user # Added import for authentication functions
import io

def login_signup_section():
    """Display login/signup interface"""
    st.title("📱 WhatsApp Automation Tool")

    # Create tabs for login and signup
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    # Get database session
    db = next(get_db())

    # Login tab
    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not username or not password:
                st.error("Please enter both username and password")
                return

            user = authenticate_user(username, password, db)
            if user:
                login_user(user)
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # Signup tab
    with tab2:
        st.header("Sign Up")
        email = st.text_input("Email", key="signup_email")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")

        if st.button("Sign Up"):
            if not all([email, username, password, confirm_password]):
                st.error("Please fill in all fields")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            user = create_user(email, username, password, db)
            if user:
                st.success("Account created successfully! Please log in.")
            else:
                st.error("Username or email already exists")

def settings_section():
    """Display and handle the settings section"""
    with st.sidebar:
        st.header("📱 WhatsApp API Settings")

        # Get current user
        user = st.session_state.user

        # Display logout button
        if st.button("Logout"):
            logout_user()
            st.rerun()

        # Get credentials from user
        instance_id = st.text_input(
            "Instance ID",
            value=user.instance_id if user and user.instance_id else "",
            type="password",
            help="Enter your WhatsApp gateway instance ID"
        )

        client_id = st.text_input(
            "Access Token",
            value=user.client_id if user and user.client_id else "",
            type="password",
            help="Enter your WhatsApp API access token"
        )

        # Save button
        if st.button("Save Credentials"):
            # Update user credentials in database
            db = next(get_db())
            user = db.query(User).filter(User.id == st.session_state.user.id).first()
            user.instance_id = instance_id
            user.client_id = client_id
            db.commit()

            # Update session state
            st.session_state.instance_id = instance_id
            st.session_state.client_id = client_id
            st.session_state.is_configured = bool(instance_id and client_id)
            st.success("✅ Credentials saved successfully!")

def main():
    st.set_page_config(page_title="WhatsApp Automation Tool", page_icon="📱")
    init_session_state()

    # Show login/signup if not authenticated
    if not st.session_state.is_authenticated:
        login_signup_section()
        return

    # Display settings sidebar and main interface for authenticated users
    settings_section()

    st.title("📱 WhatsApp Message Automation")
    st.markdown("""
    Upload your Excel/CSV file with the following columns:
    - Mobile Number
    - Name
    - Message (URL encoded text)
    - Attachment (URL link)
    - Time (delay in minutes)
    """)

    if not st.session_state.instance_id or not st.session_state.client_id:
        st.warning("⚠️ Please configure your WhatsApp API credentials in the sidebar before sending messages.")
        return

    # File uploader
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        try:
            # Read the file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Validate columns
            valid_columns, missing_columns = DataProcessor.validate_file_columns(df)

            if not valid_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
                return

            # Process dataframe
            df = DataProcessor.process_dataframe(df)

            # Preview data
            st.subheader("Data Preview")
            st.dataframe(df[['Mobile Number', 'Name', 'Message', 'Time']].head())

            # Message preview
            with st.expander("Message Preview"):
                sample_message = df['Message'].iloc[0]
                sample_name = df['Name'].iloc[0]
                st.text_area("Sample Message", sample_message, height=100)

            # Start sending messages
            if st.button("Start Sending Messages"):
                # Initialize WhatsApp sender with user credentials
                whatsapp_sender = WhatsAppSender(
                    instance_id=st.session_state.instance_id,
                    client_id=st.session_state.client_id
                )

                # Create placeholders for status displays
                progress_bar = st.progress(0)
                status_text = st.empty()
                current_operation = st.empty()

                # Create columns for success and failure counts
                col1, col2 = st.columns(2)
                success_count = col1.empty()
                failure_count = col2.empty()

                # Initialize counters
                successes = 0
                failures = 0

                # Create expanders for success and failure logs
                with st.expander("Detailed Status Log", expanded=True):
                    status_log = st.empty()

                status_updates = []

                for index, row in df.iterrows():
                    # Update current operation
                    current_operation.info(f"Processing message {index + 1} of {len(df)}")
                    recipient_info = f"📱 Sending to: {row['Name']} ({row['Mobile Number']})"
                    status_text.write(recipient_info)

                    # Validate row
                    is_valid, error_message = DataProcessor.validate_row(row)

                    if not is_valid:
                        df.at[index, 'status'] = 'failed'
                        df.at[index, 'error_message'] = error_message
                        failures += 1
                        status_updates.append(f"❌ Failed: {recipient_info} - {error_message}")
                    else:
                        # Send message
                        result = whatsapp_sender.send_message(
                            dest_number=row['Mobile Number'],
                            message=row['Message'],
                            media_url=row['Attachment'] if pd.notna(row['Attachment']) else None
                        )

                        # Update status
                        if result['success']:
                            df.at[index, 'status'] = 'sent'
                            successes += 1
                            status_updates.append(f"✅ Success: {recipient_info}")
                        else:
                            df.at[index, 'status'] = 'failed'
                            df.at[index, 'error_message'] = result.get('error', 'Unknown error')
                            failures += 1
                            status_updates.append(f"❌ Failed: {recipient_info} - {result.get('error', 'Unknown error')}")

                    # Update counters and progress
                    success_count.metric("Successful", successes)
                    failure_count.metric("Failed", failures)
                    progress = (index + 1) / len(df)
                    progress_bar.progress(progress)

                    # Update status log
                    status_log.markdown('\n'.join(status_updates))

                    # Time delay
                    if index < len(df) - 1:  # Don't delay after last message
                        delay_time = float(row['Time']) * 60
                        if delay_time > 0:
                            with st.spinner(f'Waiting {row["Time"]} minutes before next message...'):
                                time.sleep(delay_time)

                # Show final results
                st.success("Message sending completed!")

                # Display final results table
                st.subheader("Results Summary")
                st.dataframe(df[['Name', 'Mobile Number', 'status', 'error_message']])

                # Download results
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download Results CSV",
                    data=csv,
                    file_name="whatsapp_results.csv",
                    mime="text/csv"
                )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()