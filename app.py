import streamlit as st
from main import NewsletterGenerator
import os
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="AI Newsletter Generator",
    page_icon="📰",
    layout="wide"
)

# Initialize session state for history
if 'newsletter_history' not in st.session_state:
    st.session_state.newsletter_history = []

# Title and description
st.title("📰 AI Newsletter Generator")
st.markdown("""
Generate professional newsletters on any topic using AI agents!  
Powered by **CrewAI** with **Groq** (Free & Fast) and **Serper** search.
""")

# Sidebar for API key setup
with st.sidebar:
    st.header("⚙️ Setup")
    st.markdown("""
    ### Get Your FREE API Keys:
    
    1. **Groq API Key** (FREE)
       - Visit: [console.groq.com](https://console.groq.com)
       - Sign up with Google/GitHub
       - No credit card needed!
    
    2. **Serper API Key** (FREE)
       - Visit: [serper.dev](https://serper.dev)
       - Sign up with Google
       - Get 2,500 free searches!
    """)
    
    st.divider()
    
    # Check if API keys are set
    groq_key = os.getenv("GROQ_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")
    
    if groq_key and serper_key:
        st.success("✅ API keys configured!")
    else:
        st.warning("⚠️ Please add API keys to Streamlit secrets")
        st.info("""
        Go to: Settings → Secrets  
        Add:
        ```
        GROQ_API_KEY = "your_key"
        SERPER_API_KEY = "your_key"
        ```
        """)
    
    st.divider()
    
    # Newsletter History
    st.subheader("📚 History")
    if st.session_state.newsletter_history:
        st.caption(f"Generated: {len(st.session_state.newsletter_history)} newsletters")
        
        for idx, item in enumerate(reversed(st.session_state.newsletter_history[-5:])):
            with st.expander(f"📄 {item['topic'][:30]}..."):
                st.caption(f"Created: {item['timestamp']}")
                if st.button(f"Load", key=f"load_{idx}"):
                    st.session_state.loaded_newsletter = item
                    st.rerun()
    else:
        st.caption("No history yet")

# Main content
st.divider()

# Quick examples
st.subheader("💡 Quick Examples")
example_col1, example_col2, example_col3 = st.columns(3)

with example_col1:
    if st.button("🤖 AI & Technology", use_container_width=True):
        st.session_state.example_topic = "Latest developments in AI and machine learning"

with example_col2:
    if st.button("🌍 Climate & Sustainability", use_container_width=True):
        st.session_state.example_topic = "Recent climate tech innovations and green energy"

with example_col3:
    if st.button("💼 Business & Startups", use_container_width=True):
        st.session_state.example_topic = "Startup funding trends and unicorn companies"

st.divider()

# Input section
topic = st.text_input(
    "🔍 Enter Newsletter Topic:",
    value=st.session_state.get('example_topic', ''),
    placeholder="e.g., Latest developments in AI, Climate tech innovations, etc.",
    help="Enter any topic you want to create a newsletter about"
)

# Advanced options in expander
with st.expander("⚙️ Advanced Options"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        tone = st.selectbox(
            "Writing Tone:",
            ["Professional", "Casual", "Technical", "Inspirational", "Humorous"],
            help="Choose the tone of your newsletter"
        )
    
    with col2:
        length = st.selectbox(
            "Newsletter Length:",
            ["Short (500 words)", "Medium (1000 words)", "Long (1500+ words)"],
            index=1,
            help="Choose how detailed the newsletter should be"
        )
    
    with col3:
        focus = st.selectbox(
            "Content Focus:",
            ["Balanced", "News-heavy", "Analysis-heavy", "Tutorial-style"],
            help="Choose the focus of the content"
        )
    
    # Additional customization
    col4, col5 = st.columns(2)
    
    with col4:
        include_images = st.checkbox("📸 Suggest image placeholders", value=True)
        include_cta = st.checkbox("📢 Include call-to-action", value=True)
    
    with col5:
        include_stats = st.checkbox("📊 Emphasize statistics", value=True)
        include_quotes = st.checkbox("💬 Include expert quotes", value=True)

# Template selection
st.subheader("📋 Newsletter Template")
template = st.radio(
    "Choose a template:",
    ["Standard", "Tech News", "Business Weekly", "Research Digest", "Custom"],
    horizontal=True,
    help="Pre-built templates for different newsletter styles"
)

# Custom template option
if template == "Custom":
    custom_sections = st.text_area(
        "Define your sections (one per line):",
        value="Welcome\nMain Story\nFeatured Content\nQuick Updates\nSources",
        height=150
    )

generate_button = st.button("✨ Generate Newsletter", type="primary", use_container_width=True)

# Generate newsletter
if generate_button:
    if not topic:
        st.error("⚠️ Please enter a topic!")
    elif not (os.getenv("GROQ_API_KEY") and os.getenv("SERPER_API_KEY")):
        st.error("⚠️ Please configure API keys in Streamlit secrets!")
    else:
        # Prepare customization parameters
        customization = {
            "tone": tone,
            "length": length,
            "focus": focus,
            "include_images": include_images,
            "include_cta": include_cta,
            "include_stats": include_stats,
            "include_quotes": include_quotes,
            "template": template,
            "custom_sections": custom_sections if template == "Custom" else None
        }
        
        with st.spinner("🤖 AI agents are researching and writing your newsletter..."):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🔍 Researching latest information...")
                progress_bar.progress(25)
                
                result = NewsletterGenerator(topic, customization)
                
                status_text.text("✍️ Writing newsletter content...")
                progress_bar.progress(75)
                
                if result["status"] == "success":
                    progress_bar.progress(100)
                    status_text.text("✅ Newsletter generated successfully!")
                    
                    # Save to history
                    st.session_state.newsletter_history.append({
                        "topic": topic,
                        "content": result["content"],
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "customization": customization
                    })
                    
                    # Display the newsletter in tabs
                    st.divider()
                    
                    tab1, tab2, tab3 = st.tabs(["📰 Preview", "📝 Markdown", "📊 Analytics"])
                    
                    with tab1:
                        st.markdown(result["content"])
                    
                    with tab2:
                        st.code(result["content"], language="markdown")
                    
                    with tab3:
                        # Newsletter analytics
                        word_count = len(result["content"].split())
                        char_count = len(result["content"])
                        reading_time = word_count // 200  # Average reading speed
                        
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Word Count", f"{word_count:,}")
                        col2.metric("Characters", f"{char_count:,}")
                        col3.metric("Reading Time", f"{reading_time} min")
                        col4.metric("Sections", result["content"].count("##"))
                        
                        # SEO Score (simplified)
                        st.subheader("📈 Content Quality Metrics")
                        
                        has_headers = result["content"].count("#") > 3
                        has_links = "[" in result["content"] and "](" in result["content"]
                        good_length = 500 < word_count < 2000
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Headers", "✅" if has_headers else "⚠️")
                        col2.metric("External Links", "✅" if has_links else "⚠️")
                        col3.metric("Length", "✅" if good_length else "⚠️")
                    
                    # Download options
                    st.divider()
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.download_button(
                            label="📥 Download Markdown",
                            data=result["content"],
                            file_name=f"newsletter_{topic.replace(' ', '_')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Convert to HTML for email
                        html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="utf-8">
                            <style>
                                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
                                h1 {{ color: #333; }}
                                h2 {{ color: #666; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
                                a {{ color: #0066cc; }}
                            </style>
                        </head>
                        <body>
                            {result["content"].replace('#', '<h1>').replace('##', '</h1><h2>').replace('\n', '<br>')}
                        </body>
                        </html>
                        """
                        st.download_button(
                            label="📧 Download HTML",
                            data=html_content,
                            file_name=f"newsletter_{topic.replace(' ', '_')}.html",
                            mime="text/html",
                            use_container_width=True
                        )
                    
                    with col3:
                        # Plain text version
                        plain_text = result["content"].replace("#", "").replace("*", "")
                        st.download_button(
                            label="📄 Download TXT",
                            data=plain_text,
                            file_name=f"newsletter_{topic.replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    
                    # Share options
                    st.divider()
                    st.subheader("🔗 Share Your Newsletter")
                    share_col1, share_col2 = st.columns(2)
                    
                    with share_col1:
                        if st.button("📋 Copy to Clipboard", use_container_width=True):
                            st.code(result["content"])
                            st.success("Content ready to copy!")
                    
                    with share_col2:
                        if st.button("✉️ Email Template", use_container_width=True):
                            st.info("Use the HTML download for email newsletters!")
                
                else:
                    progress_bar.progress(100)
                    st.error(f"❌ Error: {result['content']}")
                    
            except Exception as e:
                progress_bar.progress(100)
                st.error(f"❌ Error generating newsletter: {str(e)}")
                st.info("💡 Make sure your API keys are correct and try again.")
                
                # Debug info in expander
                with st.expander("🔍 Debug Information"):
                    st.code(str(e))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Built with ❤️ using CrewAI, Groq, and Streamlit</p>
    <p style='font-size: 0.8em;'>Free tier: Groq (unlimited requests) + Serper (2,500 searches)</p>
</div>
""", unsafe_allow_html=True)
