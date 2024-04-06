import streamlit as st
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.document_transformers import Html2TextTransformer

def preprocess_text(text):
    text = text.replace('\n', '').replace('\\', '')
    text = text.replace('\'', "'").replace('"', '"')
    text = text.replace('\\', '')
    return text

def generate_content(c, schemas):
    results = {}
    for schema in schemas:
        prompt = ChatPromptTemplate.from_messages(
            [("human", f"You are an extractor.You will be given a string {c}.Your task is to extract the {schema} from the {c}.Dont output anything twice and every {schema} provide only the output what is mention in {schema}.The output in one {schema} shouldnot be repeated to another {schema}.Provide the output in JSON format.And dont write anything extra out of {schema}.")]
        )
        chain = prompt | chat
        content = ""
        for chunk in chain.stream({"c": c}):  # Pass the HTML content as context
            content += chunk.content
        results[schema] = content.strip()
    return results

def main():
    st.title("Schema Extraction from Web Page")
    url = st.text_input("Enter the URL:")
    schemas_input = st.text_input("Enter the schemas you want to apply, separated by commas:")
    schemas = [schema.strip() for schema in schemas_input.split(',')]
    
    if st.button("Extract"):
        # Load HTML content
        loader = AsyncHtmlLoader([url])
        docs = loader.load()
        html2text = Html2TextTransformer()
        docs_transformed = html2text.transform_documents(docs)
        html_content = docs_transformed[0].page_content
        
        # Preprocess the text
        preprocessed_text = preprocess_text(html_content)
        
        # Generate content based on schemas
        results = generate_content(preprocessed_text, schemas)
        
        # Display results
        for schema, result in results.items():
            st.subheader(schema)
            st.json(result)

if __name__ == "__main__":
    # Setup ChatAnthropic
    chat = ChatAnthropic(
        temperature=0,
        anthropic_api_key=st.secrets["key"],
        model_name="claude-3-opus-20240229"
    )
    
    main()
