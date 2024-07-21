import requests
from includes import message
from includes import write_output
from includes import payload_url
from urllib.parse import urlparse, urljoin

def openscan(url, output=None):
    try:
        with requests.Session() as session:
            payload_path = payload_url.payl()
            with open(payload_path, 'r', encoding='utf-8') as f:
                payloads = f.read().splitlines()
                
                parsed_url = urlparse(url)
                vulnerable_links = []  
                

                for payload in payloads:
                    
                    test_url = urljoin(url, parsed_url.path + 'redirect?url=' + payload)
                    try:
                        response = session.get(test_url, allow_redirects=True, timeout=5)
                        print("Checking the url ----->", test_url)
                        if response.status_code >= 300 :
                            output_msg = f"Vulnerable URL: {test_url}\n"
                            print(output_msg)
                            vulnerable_links.append(output_msg)

                            if output:
                                write_output.write(output, output_msg)
                    except requests.RequestException as e:
                        print(f'Error accessing URL -> {test_url}: {e}')

                if vulnerable_links:
                    message.send_message("\n".join(vulnerable_links))
                else:
                    print("No vulnerable URLs found.\n")

    except requests.exceptions.RequestException as e:
        print(f"Check Network Connection: {e}")

    except KeyboardInterrupt:
        print("\nScan interrupted by user.")

