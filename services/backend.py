import httpx
import time
from datetime import datetime
import streamlit as st
from utils import base64_to_image,parse_json_payload

def fetch_report(api_mapper: str, payload: dict, output_file: str = None):
    base_ip= "34.0.149.91"

    apis = {
        "mt_executive_summary": f"http://{base_ip}:8001/api/mt/executive_summary",
        "gt_llm_input": f"http://{base_ip}:8001/api/gt/llm_input",
        "mt_territory_report": f"http://{base_ip}:8001/api/mt/territory_report",
        "gt_executive_summary": f"http://{base_ip}:8001/api/gt/executive_summary",
        "gt_territory_report": f"http://{base_ip}:8001/api/gt/territory_report",
    }
    api_url=apis[api_mapper]
    """Send HTTP request to backend and return bytes/json."""
    with httpx.Client(timeout=None) as client:
        if "llm_input" in api_url:
            response = client.post(api_url, json=payload)
            response.raise_for_status()
            return response.json()
        else:
            with client.stream("POST", api_url, json=payload) as response:
                response.raise_for_status()
                if output_file:
                    with open(output_file, "wb") as f:
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                    return None
                return b"".join(response.iter_bytes())
            

      

def run_backend_sync(payload: dict, image_location: str = "", max_retries: int = 3, ):
    """Send payload to backend for text, image, or text+image generation with retries."""
   
    output_type, image_prompt, text_prompt, product_data = parse_json_payload(payload)
    start_time = datetime.now()
    base_ip="34.0.149.91"

    
    backend_map= {
    "text": f"http://{base_ip}:8000/api/text_new",
    "image": f"http://{base_ip}:8000/api/image_new",
    "text_image": f"http://{base_ip}:8000/api/image_and_text_new"
}     

    json_payload_map = {
        "text": {"text_prompt": text_prompt, "product_data": product_data},
        "image": {"image_prompt": image_prompt, "product_data": product_data, "image": image_location},
        "text_image": {"image_prompt": image_prompt, "text_prompt": text_prompt, "product_data": product_data, "image": image_location}
    }

    for attempt in range(1, max_retries + 1):
        try:
            response = httpx.post(backend_map[output_type], json=json_payload_map[output_type], timeout=300.0)

            if response.status_code != 200:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                st.error(f"❌ Backend returned status {response.status_code}: {error_msg}")
                return

            result = response.json()
            break

        except (httpx.RequestError, httpx.TimeoutException) as e:
            if attempt == max_retries:
                st.error("❌ Maximum retry attempts reached. Please try again later.")
                return
            time.sleep(2 ** attempt)

    # Display results
    if output_type == "text":
        for i in range(1, 4):
            text_dict=result.get(f"output_{i}", "")
            for k, v in text_dict.items():
                    st.markdown(f"**{k}**")
                    st.write(v)
                    st.markdown("---")  # separator line

    elif output_type == "image":
        for i in range(1, 4):
            st.image(base64_to_image(result.get(f"result{i}", "")))

    elif output_type == "text_image":
        for i in range(1, 4):
            text_dict=result['text'].get(f"output_{i}", "")
            for k, v in text_dict.items():
                    st.markdown(f"**{k}**")
                    st.write(v)
                    st.markdown("---")  # separator line
            st.image(base64_to_image(result['image_result'].get(f"result{i}", "")))

    elapsed = (datetime.now() - start_time).total_seconds() / 60
    st.success(f"✅ Total time taken: {elapsed:.2f} minutes")
