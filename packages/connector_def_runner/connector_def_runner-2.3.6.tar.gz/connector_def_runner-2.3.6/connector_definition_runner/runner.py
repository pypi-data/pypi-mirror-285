import chevron
import json
import xmltodict
from requests import JSONDecodeError
from .authenticate import Authenticate
from .attachments import parse_attachment_output


class Runner(Authenticate):

    def run(self, inputs, action_schema):
        if self.auth_error:
            return self.parse_response(self.auth_error_response, action_schema)
        response = self.session.request(
            method=self.get_method(inputs, action_schema['meta']),
            url=self._join_url(self.url, self.get_endpoint(inputs, action_schema['meta'])),
            **self.get_kwargs(inputs, action_schema['meta'])
        )
        response.raise_for_status()
        resp = self.parse_response(response, action_schema)
        return resp

    @staticmethod
    def get_method(inputs=None, action_meta=None):
        return action_meta['method']

    @staticmethod
    def get_endpoint(inputs, action_meta):
        # Mustache if available, if not returns string as is.
        return chevron.render(action_meta['endpoint'], inputs.get('path_parameters', {}))

    def get_kwargs(self, inputs, action_meta=None):
        # todo can we handle files automatically.
        self.params.update(inputs.get('parameters', {}))
        if "headers" in action_meta:
            headers = action_meta['headers']
            self._format_headers(headers, inputs)
            headers.update(inputs.get('headers', {}))
            inputs['headers'] = headers
        return {
            'params': self.params,
            'data': inputs.get('data_body'),
            'json': inputs.get('json_body'),
            'files': inputs.get('files'),
            'headers': inputs.get('headers')
        }

    def parse_response(self, response, action_schema):
        output = {
            'status_code': response.status_code,
            'response_headers': dict(response.headers),
            'reason': response.reason
        }
        if response.status_code < 300:
            # Only create an attachment if we have a successful response
            file = parse_attachment_output(response, action_schema)
            if file:
                output['file'] = file
        output_type = action_schema["meta"].get("outputType", "json")
        if output_type == "xml":
            output["json_body"] = xmltodict.parse(response.text)
        else:
            try:
                output['json_body'] = response.json()
            except JSONDecodeError:
                if 'file' not in output:
                    # Avoids the duplication of the file content in response_text
                    output['response_text'] = response.text
        return output
