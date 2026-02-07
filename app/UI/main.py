"""
Agentic Issue Tracker - Streamlit Version
AI-Powered Issue Management System
"""
import requests
import streamlit as st
import json
import uuid
from datetime import datetime, timedelta
import time
from urllib.parse import quote

# Page config
st.set_page_config(
    page_title="Agentic Issue Tracker",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }

    .issue-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .priority-urgent {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .priority-high {
        background-color: #fed7aa;
        color: #9a3412;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .priority-medium {
        background-color: #fef3c7;
        color: #92400e;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .priority-low {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    }

    .tag-badge {
        background-color: #f3f4f6;
        color: #374151;
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-right: 0.5rem;
        display: inline-block;
    }

    .ai-hint {
        background: linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%);
        border: 1px solid #e9d5ff;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }

    .chat-message-user {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        max-width: 70%;
        margin-left: auto;
    }

    .chat-message-ai {
        background: white;
        border: 1px solid #e2e8f0;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        max-width: 70%;
    }

    .status-open {
        color: #6b7280;
    }

    .status-in-progress {
        color: #2563eb;
    }

    .status-resolved {
        color: #16a34a;
    }

    .status-closed {
        color: #9ca3af;
    }
</style>
""", unsafe_allow_html=True)

def fetch_issues():
    response = requests.get("http://127.0.0.1:8000/api/issues/issues?skip=0&limit=100")
    response.raise_for_status()
    return response.json()

def create_issue(query:str):
    response = requests.post(f"http://127.0.0.1:8000/api/issues/issues?query={query}")
    response.raise_for_status()
    return response.json()

def update_issue(query:str):
    response = requests.put(f"http://127.0.0.1:8000/api/issues/issue?query={query}")
    response.raise_for_status()
    return response.json()


# Initialize session state
if 'issues' not in st.session_state:
    st.session_state.issues = fetch_issues()

    # st.session_state.issues = [
    #     {
    #         'id': '1',
    #         'title': 'Login crashes on wrong OTP',
    #         'description': 'Application terminates unexpectedly when user enters incorrect OTP during authentication flow',
    #         'priority': 'urgent',
    #         'status': 'open',
    #         'tags': ['bug', 'security', 'ui'],
    #         'estimated_time': '4 hours',
    #         'root_cause_hint': 'Unhandled exception in OTP validation logic',
    #         'created': '2 hours ago'
    #     },
    #     {
    #         'id': '2',
    #         'title': 'Slow dashboard loading',
    #         'description': 'Dashboard takes 5+ seconds to load with large datasets',
    #         'priority': 'high',
    #         'status': 'in_progress',
    #         'tags': ['performance', 'backend'],
    #         'estimated_time': '2 days',
    #         'root_cause_hint': None,
    #         'created': '1 day ago'
    #     },
    #     {
    #         'id': '3',
    #         'title': 'Add dark mode support',
    #         'description': 'Users requesting dark mode theme option',
    #         'priority': 'medium',
    #         'status': 'open',
    #         'tags': ['feature', 'ui'],
    #         'estimated_time': '1 week',
    #         'root_cause_hint': None,
    #         'created': '3 days ago'
    #     }
    # ]

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {
            'role': 'assistant',
            'content': "Hi! I can help you update issues. Try commands like:\n• Mark issue #1 as resolved\n• Change priority of issue #2 to high\n• Close issue #3"
        }
    ]


# Helper functions
def get_priority_badge(priority):
    """Return HTML for priority badge"""
    return f'<span class="priority-{priority}">{priority.upper()}</span>'


def get_status_icon(status):
    """Return emoji for status"""
    icons = {
        'open': '⭕',
        'in_progress': '🔄',
        'resolved': '✅',
        'closed': '✅'
    }
    return icons.get(status, '⭕')


def get_status_color_class(status):
    """Return CSS class for status color"""
    return f"status-{status.replace('_', '-')}"


def simulate_ai_creation(nl_input):
    """Simulate AI processing to create issue from natural language"""
    time.sleep(2)  # Simulate AI processing

    # Simple keyword-based extraction (in production, use real LLM)
    title = nl_input[:50] + "..." if len(nl_input) > 50 else nl_input

    # Determine priority based on keywords
    priority = 'medium'
    if any(word in nl_input.lower() for word in ['urgent', 'critical', 'asap', 'immediately']):
        priority = 'urgent'
    elif any(word in nl_input.lower() for word in ['important', 'high', 'priority']):
        priority = 'high'
    elif any(word in nl_input.lower() for word in ['low', 'minor', 'nice to have']):
        priority = 'low'

    # Extract tags
    tags = []
    if 'bug' in nl_input.lower() or 'crash' in nl_input.lower() or 'error' in nl_input.lower():
        tags.append('bug')
    if 'feature' in nl_input.lower() or 'add' in nl_input.lower():
        tags.append('feature')
    if 'performance' in nl_input.lower() or 'slow' in nl_input.lower():
        tags.append('performance')
    if 'security' in nl_input.lower():
        tags.append('security')
    if 'ui' in nl_input.lower() or 'interface' in nl_input.lower():
        tags.append('ui')
    if 'backend' in nl_input.lower() or 'api' in nl_input.lower():
        tags.append('backend')

    if not tags:
        tags = ['general']

    new_issue = {
        'id': str(len(st.session_state.issues) + 1),
        'title': title,
        'description': f"AI-generated from: {nl_input}",
        'priority': priority,
        'status': 'open',
        'tags': tags,
        'estimated_time': '4 hours',
        'root_cause_hint': None,
        'created': 'Just now'
    }

    return new_issue

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🤖 Agentic Issue Tracker</h1>
        <p>AI-Powered Issue Management System</p>
    </div>
    """, unsafe_allow_html=True)

    # Sidebar navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.radio(
        "Select Section",
        ["📋 Issues", "✨ AI Creator", "💬 Chat Updater"],
        label_visibility="collapsed"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Total Issues:** {len(st.session_state.issues)}")

    # Count by status
    status_counts = {}
    for issue in st.session_state.issues:
        status = issue['status']
        status_counts[status] = status_counts.get(status, 0) + 1

    st.sidebar.markdown("**By Status:**")
    for status, count in status_counts.items():
        st.sidebar.markdown(f"• {status.replace('_', ' ').title()}: {count}")

    # Count by priority
    priority_counts = {}
    for issue in st.session_state.issues:
        priority = issue['priority']
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    st.sidebar.markdown("**By Priority:**")
    for priority in ['urgent', 'high', 'medium', 'low']:
        count = priority_counts.get(priority, 0)
        if count > 0:
            st.sidebar.markdown(f"• {priority.title()}: {count}")

    # Page content
    if page == "📋 Issues":
        show_issues_page()
    elif page == "✨ AI Creator":
        show_ai_creator_page()
    elif page == "💬 Chat Updater":
        show_chat_updater_page()


def show_issues_page():
    """Display all issues"""
    st.header("📋 All Issues")

    # Filters
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        status_filter = st.multiselect(
            "Filter by Status",
            options=['open', 'in_progress', 'resolved', 'closed'],
            default=['open', 'in_progress']
        )

    with col2:
        priority_filter = st.multiselect(
            "Filter by Priority",
            options=['urgent', 'high', 'medium', 'low'],
            default=['urgent', 'high', 'medium', 'low']
        )

    with col3:
        sort_by = st.selectbox(
            "Sort by",
            options=['Created (newest)', 'Created (oldest)', 'Priority', 'Status']
        )

    st.markdown("---")

    # Filter issues
    filtered_issues = [
        issue for issue in st.session_state.issues
        if issue['status'] in status_filter and issue['priority'] in priority_filter
    ]

    # Sort issues
    if sort_by == 'Priority':
        priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
        filtered_issues.sort(key=lambda x: priority_order.get(x['priority'], 4))

    if not filtered_issues:
        st.info("No issues match the selected filters.")
        return

    # Display issues
    for issue in filtered_issues:
        with st.container():
            col1, col2 = st.columns([8, 2])

            with col1:
                # Title and status
                st.markdown(f"### {get_status_icon(issue['status'])} {issue['title']}")
                st.markdown(f"<small>Issue #{issue['issue_id']} • {issue['created_at']}</small>", unsafe_allow_html=True)

            with col2:
                st.markdown(get_priority_badge(issue['priority']), unsafe_allow_html=True)

            # Description
            st.markdown(f"**Description:** {issue['description']}")

            # Tags
            tags_html = " ".join([f'<span class="tag-badge">🏷️ {tag}</span>' for tag in issue['tags']])
            st.markdown(tags_html, unsafe_allow_html=True)

            # Metadata
            col2, col3 = st.columns(2)
            # with col1:
            #     st.markdown(f"⏱️ **Estimated:** {issue['estimated_time']}")
            with col2:
                st.markdown(f"📊 **Status:** {issue['status'].replace('_', ' ').title()}")
            with col3:
                st.markdown(f"🎯 **Priority:** {issue['priority'].title()}")

            # Root cause hint (if available)
            if issue.get('root_cause_hint'):
                st.markdown(f"""
                <div class="ai-hint">
                    <strong>🤖 AI Root Cause Analysis</strong><br/>
                    {issue['root_cause_hint']}
                </div>
                """, unsafe_allow_html=True)

            # Action buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button(f"Edit #{issue['issue_id']}", key=f"edit_{issue['issue_id']}"):
                    st.info(f"Edit functionality for issue #{issue['id']}")
            with col2:
                if st.button(f"Mark Resolved #{issue['issue_id']}", key=f"resolve_{issue['issue_id']}"):
                    issue['status'] = 'resolved'
                    st.success(f"Issue #{issue['id']} marked as resolved!")
                    st.rerun()
            with col3:
                if st.button(f"Close #{issue['issue_id']}", key=f"close_{issue['issue_id']}"):
                    issue['status'] = 'closed'
                    st.success(f"Issue #{issue['id']} closed!")
                    st.rerun()
            with col4:
                if st.button(f"Delete #{issue['issue_id']}", key=f"delete_{issue['issue_id']}"):
                    st.session_state.issues = [i for i in st.session_state.issues if i['issue_id'] != issue['issue_id']]
                    st.success(f"Issue #{issue['issue_id']} deleted!")
                    st.rerun()

            st.markdown("---")


def show_ai_creator_page():
    """AI-powered issue creation"""
    st.header("✨ AI Issue Creator")
    st.markdown("Describe your issue in natural language, and AI will structure it for you!")

    # Info box
    st.info("""
    **AI will automatically:**
    - Extract a clear, concise title
    - Generate detailed description
    - Assign appropriate priority (low/medium/high/urgent)
    - Add relevant tags (bug, ui, backend, security, etc.)
    - Estimate resolution time
    """)

    # Example inputs
    with st.expander("📝 See Example Inputs"):
        examples = [
            "App crashes on login when user enters wrong OTP, urgent bug",
            "Payment gateway times out after 30 seconds, urgent issue",
            "Users can't upload files larger than 5MB, feature request",
            "Dashboard is slow with 10k+ records, performance problem"
        ]
        for i, example in enumerate(examples):
            if st.button(example, key=f"example_{i}"):
                st.session_state.nl_input = example

    # Input area
    nl_input = st.text_area(
        "Describe your issue (natural language):",
        value=st.session_state.get('nl_input', ''),
        height=150,
        placeholder="Example: App crashes on login when user enters wrong OTP, this is urgent and blocks all users from accessing the system"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        create_button = st.button("🚀 Create with AI", type="primary", use_container_width=True)
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.nl_input = ''
            st.rerun()

    if create_button and nl_input.strip():
        with st.spinner("🤖 AI is processing your input..."):
            # Simulate AI processing
            new_issue = create_issue(nl_input.strip())

            # Add to issues
            st.session_state.issues.insert(0, new_issue)

            st.success("✅ Issue created successfully!")

            # Show created issue
            st.markdown("### 📄 Created Issue:")
            with st.container():
                st.markdown(f"**Title:** {new_issue['title']}")
                st.markdown(f"**Description:** {new_issue['description']}")
                st.markdown(f"**Priority:** {new_issue['priority'].upper()}")
                st.markdown(f"**Status:** {new_issue['status']}")
                tags_html = " ".join([f'<span class="tag-badge">🏷️ {tag}</span>' for tag in new_issue['tags']])
                st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
                # st.markdown(f"**Estimated Time:** {new_issue['estimated_time']}")

            # Clear input
            st.session_state.nl_input = ''

            if st.button("➕ Create Another Issue"):
                st.rerun()

            if st.button("📋 View All Issues"):
                st.session_state.page = "Issues"
                st.rerun()


def show_chat_updater_page():
    """Chat-based issue updater"""
    st.header("💬 AI Issue Updater")
    st.markdown("Update issues using natural language commands!")

    # Info box
    st.info("""
    **Supported Commands:**
    - Mark issue #1 as resolved
    - Change priority of issue #2 to high
    - Close issue #3
    - Set issue #1 to in progress
    """)

    # Chat history
    st.markdown("### 💬 Chat History")

    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message-user">
                    <strong>You:</strong><br/>
                    {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message-ai">
                    <strong>🤖 AI Assistant:</strong><br/>
                    {message['content'].replace(chr(10), '<br/>')}
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")

    # Input area
    st.markdown("### ✍️ Enter Command")

    user_input = st.text_input(
        "Type your command:",
        placeholder="Example: Mark issue #1 as resolved and change priority to medium",
        label_visibility="collapsed"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        send_button = st.button("📤 Send", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = [
                {
                    'role': 'assistant',
                    'content': "Chat cleared! How can I help you update your issues?"
                }
            ]
            st.rerun()

    if send_button and user_input.strip():
        # Add user message
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input
        })

        with st.spinner("🤖 Processing command..."):
            # Process command
            result = update_issue(quote(user_input))

            # if result['success']:
            #     response = result['message']
            # else:
            #     response = f"❌ {result['message']}"

            # Add AI response
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': result
            })

        st.rerun()

    # Quick actions
    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")

    # Get open issues
    open_issues = [i for i in st.session_state.issues if i['status'] in ['open', 'in_progress']]

    if open_issues:
        issue_options = [f"#{i['issue_id']} - {i['title'][:50]}" for i in open_issues]
        selected_issue_str = st.selectbox("Select an issue:", issue_options)

        if selected_issue_str:
            issue_id = selected_issue_str.split(' - ')[0][1:]  # Extract ID

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("✅ Mark Resolved", use_container_width=True):
                    command = f"Mark issue #{issue_id} as resolved"
                    # st.session_state.chat_history.append({'role': 'user', 'content': command})
                    # result = process_chat_command(command)
                    result = update_issue(quote(command))
                    # st.session_state.chat_history.append({'role': 'assistant', 'content': result})
                    st.rerun()

            with col2:
                if st.button("🔼 Set High Priority", use_container_width=True):
                    command = f"Change priority of issue #{issue_id} to high"
                    st.session_state.chat_history.append({'role': 'user', 'content': command})
                    result = update_issue(quote(command))
                    # st.session_state.chat_history.append({'role': 'assistant', 'content': result})
                    st.rerun()

            with col3:
                if st.button("🚫 Close Issue", use_container_width=True):
                    command = f"Close issue #{issue_id}"
                    st.session_state.chat_history.append({'role': 'user', 'content': command})
                    result = update_issue(quote(command))
                    # st.session_state.chat_history.append({'role': 'assistant', 'content': result})
                    st.rerun()
    else:
        st.info("No open issues to update!")


if __name__ == "__main__":
    main()