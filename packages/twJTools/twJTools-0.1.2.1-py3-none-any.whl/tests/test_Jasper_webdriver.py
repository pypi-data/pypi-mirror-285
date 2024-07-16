from twJTools.Jasper_webdriver import WebCrawler

if __name__ == "__main__":
    driver = WebCrawler()
    try:
        pass
    except KeyboardInterrupt:
        driver.close()  # 在收到鍵盤中斷（Ctrl+C）後，手動關閉瀏覽器
