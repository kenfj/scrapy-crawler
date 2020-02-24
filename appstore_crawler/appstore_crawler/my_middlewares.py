
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message

# https://stackoverflow.com/questions/41404281
# /how-to-retry-the-request-n-times-when-an-item-gets-an-empty-field


class CustomRetryMiddleware(RetryMiddleware):

    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        # this is your check
        if (response.status == 200
            and response.url.startswith("https://apps.apple.com/us/app")
                and not response.xpath(spider.retry_xpath).get()):
            spider.logger.warning(f"RETRY {request.url}...")
            return self._retry(request, f"empty response from xpath {spider.retry_xpath}", spider) or response

        return response
