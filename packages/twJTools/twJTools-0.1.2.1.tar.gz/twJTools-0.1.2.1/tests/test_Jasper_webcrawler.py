from twJTools.Jasper_webcrawler import WebCrawler

if __name__ == "__main__":
    # 使用示例
    crawler = WebCrawler()

    # GET 請求
    url = "https://example.com"
    html_content = crawler.get_html(url)
    print(html_content)

    # POST 請求
    post_url = "https://example.com/login"
    post_data = {"username": "your_username", "password": "your_password"}
    html_content = crawler.post_html(post_url, post_data)
    print(html_content)

    # 根據CSS選擇器獲取元素
    # 1. 使用標籤名選擇器
    elements = crawler.get_element_by_css_selector(html_content, "h1")
    for element in elements:
        print(element.text)

    # 2. 使用類名選擇器
    elements = crawler.get_element_by_css_selector(html_content, ".class-name")
    for element in elements:
        print(element.text)

    # 3. 使用ID選擇器
    element = crawler.get_element_by_id(html_content, "specific-id")
    print(element.text if element else "元素未找到")

    # 4. 使用屬性選擇器
    elements = crawler.get_element_by_css_selector(html_content, '[type="text"]')
    for element in elements:
        print(element.get('value'))

    # 5. 使用組合選擇器
    elements = crawler.get_element_by_css_selector(html_content, "div.class-name")
    for element in elements:
        print(element.text)
