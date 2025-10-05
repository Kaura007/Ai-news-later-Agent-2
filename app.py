import streamlit as st
from main import NewsletterGenerator
import os
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Initialize session state
if 'newsletter_history' not in st.session_state:
    st.session_state.newsletter_history = []

# Title
st.title("📰 AI Newsletter Generator")
st.markdown("Generate professional newsletters using AI agents! Powered by **CrewAI**, **Groq**, and **Serper**.")

# Sidebar
with st.sidebar:
    st.header("⚙️ Setup")
    st.markdown("""
    ### Get Your FREE API Keys:
    
    1. **Groq** (FREE): [console.groq.com](https://console.groq.com)
    2. **Serper** (2500 free): [serper.dev](https://serper.dev)
    """)
    
    st.divider()
    
    # Check API keys
    groq_key = os.getenv("GROQ_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if groq_key and serper_key:
        st.success("✅ API keys configured!")
    else:
        st.warning("⚠️ Add API keys in Settings → Secrets")

st.divider()

# Quick examples
st.subheader("💡 Quick Examples")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🤖 AI & Tech", use_container_width=True):
        st.session_state.example_topic = "Latest AI developments"

with col2:
    if st.button("🌍 Climate", use_container_width=True):
        st.session_state.example_topic = "Climate tech innovations"

with col3:
    if st.button("💼 Business", use_container_width=True):
        st.session_state.example_topic = "Startup funding trends"

st.divider()

# Main input
topic = st.text_input(
    "🔍 Enter Newsletter Topic:",
    value=st.session_state.get('example_topic', ''),
    placeholder="e.g., Latest developments in AI"
)

# Advanced options
with st.expander("⚙️ Advanced Options"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tone = st.selectbox("Tone:", ["Professional", "Casual", "Technical", "Inspirational"])
    
    with col2:
        length = st.selectbox("Length:", ["Short (500 words)", "Medium (1000 words)", "Long (1500+ words)"], index=1)
    
    with col3:
        focus = st.selectbox("Focus:", ["Balanced", "News-heavy", "Analysis-heavy"])

# Generate button
generate_button = st.button("✨ Generate Newsletter", type="primary", use_container_width=True)

# Generate newsletter
if generate_button:
    if not topic:
        st.error("⚠️ Please enter a topic!")
    elif not (groq_key and serper_key):
        st.error("⚠️ Please configure API keys!")
    else:
        customization = {
            "tone": tone,
            "length": length,
            "focus": focus
        }
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("🔍 Researching...")
            progress_bar.progress(25)
            
            result = NewsletterGenerator(topic, customization)
            
            status_text.text("✍️ Writing...")
            progress_bar.progress(75)
            
            if result["status"] == "success":
                progress_bar.progress(100)
                status_text.text("✅ Complete!")
                
                # Save to history
                st.session_state.newsletter_history.append({
                    "topic": topic,
                    "content": result["content"],
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                
                st.divider()
                
                # Display newsletter
                tab1, tab2 = st.tabs(["📰 Preview", "📝 Markdown"])
                
                with tab1:
                    st.markdown(result["content"])
                
                with tab2:
                    st.code(result["content"], language="markdown")
                
                # Download buttons
                st.divider()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        "📥 Download Markdown",
                        result["content"],
                        f"newsletter_{topic.replace(' ', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    plain_text = result["content"].replace("#", "").replace("*", "")
                    st.download_button(
                        "📄 Download Text",
                        plain_text,
                        f"newsletter_{topic.replace(' ', '_')}.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
            else:
                st.error(f"❌ Error: {result['content']}")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            with st.expander("🔍 Debug Info"):
                st.code(str(e))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using CrewAI, Groq, and Streamlit</p>
</div>
""", unsafe_allow_html=True)
