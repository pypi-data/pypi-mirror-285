import datetime
import time
import unittest

from unittest.mock import patch, MagicMock

from aiohttp import ClientSSLError, ClientError

from smsaero import SmsAero, SmsAeroException, SmsAeroNoMoneyException, SmsAeroConnectionException

from . import DEFAULT_RESPONSE


class TestSmsAero(unittest.TestCase):
    def setUp(self):
        self.smsaero = SmsAero("admin@smsaero.ru", "test_api_key_lX8APMlgliHvkHk04i7")

    def test_default_signature_value(self):
        self.assertEqual(self.smsaero.SIGNATURE, "Sms Aero")

    def test_get_gate_urls_with_url_gate(self):
        smsaero = SmsAero("admin@smsaero.ru", "test_api_key_lX8APMlgliHvkHk04i7", url_gate="test.gate")
        result = smsaero.get_gate_urls()
        self.assertEqual(result, ["@test.gate/v2/"])

    def test_get_gate_urls_without_url_gate(self):
        smsaero = SmsAero("admin@smsaero.ru", "test_api_key_lX8APMlgliHvkHk04i7")
        result = smsaero.get_gate_urls()
        self.assertEqual(result, SmsAero.GATE_URLS)

    def test_check_and_format_user_gate_with_at_prefix(self):
        smsaero = SmsAero(
            "admin@smsaero.ru",
            "test_api_key_lX8APMlgliHvkHk04i7",
            url_gate="gate.smsaero.ru/v2",
        )
        self.assertEqual(smsaero.get_gate(), "@gate.smsaero.ru/v2/")

    def test_check_and_format_user_gate_with_v2_suffix(self):
        smsaero = SmsAero(
            "admin@smsaero.ru",
            "test_api_key_lX8APMlgliHvkHk04i7",
            url_gate="@gate.smsaero.ru",
        )
        self.assertEqual(smsaero.get_gate(), "@gate.smsaero.ru/v2/")

    def test_check_and_format_user_gate_with_correct_format(self):
        smsaero = SmsAero(
            "admin@smsaero.ru",
            "test_api_key_lX8APMlgliHvkHk04i7",
            url_gate="@gate.smsaero.ru/v2/",
        )
        self.assertEqual(smsaero.get_gate(), "@gate.smsaero.ru/v2/")

    def test_check_and_format_user_gate_with_incorrect_format(self):
        smsaero = SmsAero(
            "admin@smsaero.ru",
            "test_api_key_lX8APMlgliHvkHk04i7",
            url_gate="gate.smsaero.ru",
        )
        self.assertEqual(smsaero.get_gate(), "@gate.smsaero.ru/v2/")

    def test_fill_nums_with_single_number(self):
        number = 79031234567
        result = self.smsaero.fill_nums(number)
        self.assertEqual(result, {"number": number})

    def test_fill_nums_with_multiple_numbers(self):
        numbers = [79031234567, 9876543210]
        result = self.smsaero.fill_nums(numbers)
        self.assertEqual(result, {"numbers": numbers})

    def test_fill_nums_with_none_params(self):
        with self.assertRaises(ValueError) as context:
            self.smsaero.fill_nums(None)
        self.assertEqual(str(context.exception), "Number cannot be empty")

    @patch("aiohttp.ClientSession.post")
    def test_check_response_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        result = SmsAero.check_response(mock_response.json())
        self.assertEqual(result, False)

    @patch("aiohttp.ClientSession.post")
    def test_check_response_reject(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "reject", "reason": "test reason"}
        mock_post.return_value = mock_response

        with self.assertRaises(SmsAeroException) as context:
            SmsAero.check_response(mock_response.json())

        self.assertEqual(str(context.exception), "test reason")

    @patch("aiohttp.ClientSession.post")
    def test_check_response_no_credits(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "no credits"}
        mock_post.return_value = mock_response

        with self.assertRaises(SmsAeroNoMoneyException) as context:
            SmsAero.check_response(mock_response.json())

        self.assertEqual(str(context.exception), "no credits")

    @patch("aiohttp.ClientSession.post")
    def test_check_response_not_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False, "message": "test reason"}
        mock_post.return_value = mock_response

        with self.assertRaises(SmsAeroException) as context:
            SmsAero.check_response(mock_response.json())

        self.assertEqual(str(context.exception), "test reason")

    @patch("aiohttp.ClientSession.post")
    def test_check_response_not_success_without_message(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": False}
        mock_post.return_value = mock_response

        with self.assertRaises(SmsAeroException) as context:
            SmsAero.check_response(mock_response.json())

        self.assertEqual(str(context.exception), "Unknown error")

    def test_build_url(self):
        proto = "https"
        selector = "sms/send"
        gate = "@gate.smsaero.ru/v2/"
        page = None

        expected_url = "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send"
        actual_url = self.smsaero.build_url(proto, selector, gate, page)

        self.assertEqual(actual_url, expected_url)

    def test_build_url_with_page(self):
        proto = "http"
        selector = "sign/list"
        gate = "@gate.smsaero.ru/v2/"
        page = 1

        expected_url = "http://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sign/list?page=1"
        actual_url = self.smsaero.build_url(proto, selector, gate, page)

        self.assertEqual(actual_url, expected_url)

    @patch("aiohttp.ClientSession.post")
    async def test_request_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        result = await self.smsaero.request("sms/send", {"number": 79031234567, "text": "test message"})
        self.assertEqual(result, False)

    @patch("aiohttp.ClientSession.post")
    async def test_request_error(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "error", "message": "test reason", "success": False}
        mock_post.return_value = mock_response

        with self.assertRaises(SmsAeroException) as context:
            await self.smsaero.request("sms/send", {"number": 79031234567, "text": "test message"})

        self.assertEqual(str(context.exception), "test reason")

    @patch("aiohttp.ClientSession.post")
    async def test_request_ssl_error(self, mock_post):
        mock_post.side_effect = ClientSSLError

        with self.assertRaises(SmsAeroException):
            await self.smsaero.request("sms/send", {"number": 79031234567, "text": "test message"})

        args, _ = mock_post.call_args
        self.assertTrue(args[0].startswith("http"))
        self.assertEqual(
            args[0],
            "http://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.net/v2/sms/send",
        )

    @patch("aiohttp.ClientSession.post")
    async def test_request_connection_error(self, mock_post):
        mock_post.side_effect = ClientError

        with self.assertRaises(SmsAeroConnectionException):
            await self.smsaero.request("sms/send", {"number": 79031234567, "text": "test message"})

        args, _ = mock_post.call_args
        self.assertTrue(args[0].startswith("https"))
        self.assertEqual(
            args[0],
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.net/v2/sms/send",
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        result = await self.smsaero.send_sms(79031234567, "test message")
        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={"number": 79031234567, "text": "test message", "sign": "Sms Aero", "callbackUrl": None},
            timeout=15,
        )

    @patch.object(SmsAero, "request")
    async def test_send_sms_with_list_of_numbers(self, mock_request):
        mock_request.return_value = {"success": True}
        numbers = [79031234567, 79038805678]
        text = "Hello, World!"
        result = await self.smsaero.send_sms(numbers, text)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with(
            "sms/send", {"numbers": numbers, "text": text, "sign": self.smsaero.SIGNATURE, "callbackUrl": None}
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_with_sign(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        result = await self.smsaero.send_sms(79031234567, "test message", "test sign")
        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={"number": 79031234567, "text": "test message", "sign": "test sign", "callbackUrl": None},
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_with_initial_sign(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        smsaero = SmsAero("admin@smsaero.ru", "test_api_key_lX8APMlgliHvkHk04i7", signature="testSign")
        result = await smsaero.send_sms(79031234567, "test message")
        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={"number": 79031234567, "text": "test message", "sign": "testSign", "callbackUrl": None},
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_another_gate(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        smsaero = SmsAero(
            "admin@smsaero.ru",
            "test_api_key_lX8APMlgliHvkHk04i7",
            url_gate="@gate.test/v2/",
        )
        result = await smsaero.send_sms(79031234567, "test message")
        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.test/v2/sms/send",
            json={"number": 79031234567, "text": "test message", "sign": "Sms Aero", "callbackUrl": None},
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_with_callback_url(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        result = await self.smsaero.send_sms(
            79031234567,
            "test message",
            callback_url="https://smsaero.ru/callback",
        )
        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={
                "number": 79031234567,
                "text": "test message",
                "sign": "Sms Aero",
                "callbackUrl": "https://smsaero.ru/callback",
            },
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_with_date_to_send(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        date_to_send = datetime.datetime.now() + datetime.timedelta(days=1)
        result = await self.smsaero.send_sms(
            79031234567,
            "test message",
            date_to_send=date_to_send,
        )

        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={
                "number": 79031234567,
                "text": "test message",
                "sign": "Sms Aero",
                "callbackUrl": None,
                "dateSend": int(time.mktime(date_to_send.timetuple())),
            },
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_send_with_all_params(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        date_to_send = datetime.datetime.now() + datetime.timedelta(days=1)
        result = await self.smsaero.send_sms(
            79031234567,
            "test message",
            sign="test sign",
            callback_url="https://smsaero.ru/callback",
            date_to_send=date_to_send,
        )

        self.assertEqual(result, False)

        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/send",
            json={
                "number": 79031234567,
                "text": "test message",
                "sign": "test sign",
                "callbackUrl": "https://smsaero.ru/callback",
                "dateSend": int(time.mktime(date_to_send.timetuple())),
            },
            timeout=15,
        )

    @patch("aiohttp.ClientSession.post")
    async def test_sms_status(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = DEFAULT_RESPONSE
        mock_post.return_value = mock_response

        sms_id = 12345
        result = await self.smsaero.sms_status(sms_id)

        self.assertEqual(result, False)
        mock_post.assert_called_once_with(
            "https://admin%40smsaero.ru:test_api_key_lX8APMlgliHvkHk04i7@gate.smsaero.ru/v2/sms/status",
            json={"id": sms_id},
            timeout=15,
        )

    @patch.object(SmsAero, "request")
    async def test_sms_list_with_list_of_numbers(self, mock_request):
        mock_request.return_value = {"success": True}
        numbers = [79031234567, 79038805678]
        text = "Hello, World!"
        result = await self.smsaero.sms_list(numbers, text)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sms/list", {"numbers": numbers, "text": text}, None)

    @patch.object(SmsAero, "request")
    async def test_sms_list_with_single_number(self, mock_request):
        mock_request.return_value = {"success": True}
        number = 79031234567
        result = await self.smsaero.sms_list(number)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sms/list", {"number": number}, None)

    @patch.object(SmsAero, "request")
    async def test_sms_list_with_single_text(self, mock_request):
        mock_request.return_value = {"success": True}
        text = "Hello, World!"
        result = await self.smsaero.sms_list(text=text)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sms/list", {"text": text}, None)

    @patch.object(SmsAero, "request")
    async def test_sms_list_with_single_page(self, mock_request):
        mock_request.return_value = {"success": True}
        page = 1
        result = await self.smsaero.sms_list(page=page)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sms/list", {}, page)

    @patch.object(SmsAero, "request")
    async def test_is_authorized(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.is_authorized()
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("auth")

    @patch.object(SmsAero, "request")
    async def test_balance(self, mock_request):
        mock_request.return_value = {"balance": 100.0}
        result = await self.smsaero.balance()
        self.assertEqual(result, {"balance": 100.0})
        mock_request.assert_called_once_with("balance")

    @patch.object(SmsAero, "request")
    async def test_balance_add(self, mock_request):
        mock_request.return_value = {"result": "success", "success": True}
        amount = 100.0
        card_id = 12345

        result = await self.smsaero.balance_add(amount=amount, card_id=card_id)

        self.assertEqual(result, {"result": "success", "success": True})
        mock_request.assert_called_once_with("balance/add", {"sum": 100.0, "cardId": 12345})

    @patch.object(SmsAero, "request")
    async def test_cards(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.cards()
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("cards")

    @patch.object(SmsAero, "request")
    async def test_tariffs(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.tariffs()
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("tariffs")

    @patch.object(SmsAero, "request")
    async def test_sign_list(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.sign_list()
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sign/list", page=None)

    @patch.object(SmsAero, "request")
    async def test_sign_list_with_page(self, mock_request):
        mock_request.return_value = {"success": True}
        page = 2
        result = await self.smsaero.sign_list(page)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("sign/list", page=page)

    @patch.object(SmsAero, "request")
    async def test_group_add(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.group_add("test_group")
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("group/add", {"name": "test_group"})

    @patch.object(SmsAero, "request")
    async def test_group_delete(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.group_delete(1)
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("group/delete", {"id": 1})

    @patch.object(SmsAero, "request")
    async def test_group_delete_all(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.group_delete_all()
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("group/delete-all")

    @patch.object(SmsAero, "request")
    async def test_group_list(self, mock_request):
        mock_request.return_value = {"success": True, "data": {}}
        page = 1
        result = await self.smsaero.group_list(page)

        self.assertEqual(result, {"success": True, "data": {}})
        mock_request.assert_called_once_with("group/list", page=page)

    @patch.object(SmsAero, "request")
    async def test_contact_add(self, mock_request):
        mock_request.return_value = {
            "id": 12345,
            "number": "79031234567",
            "sex": "male",
            "lname": "Doe",
            "fname": "John",
            "sname": "Smith",
            "param1": "custom1",
            "param2": "custom2",
            "param3": "custom3",
            "operator": 5,
            "extendOperator": "BEELINE",
        }
        number = 79031234567
        group_id = 6789
        birthday = "1990-01-01"
        sex = "male"
        last_name = "Doe"
        first_name = "John"
        surname = "Smith"
        param1 = "custom1"
        param2 = "custom2"
        param3 = "custom3"

        result = await self.smsaero.contact_add(
            number=number,
            group_id=group_id,
            birthday=birthday,
            sex=sex,
            last_name=last_name,
            first_name=first_name,
            surname=surname,
            param1=param1,
            param2=param2,
            param3=param3,
        )

        self.assertEqual(
            result,
            {
                "id": 12345,
                "number": "79031234567",
                "sex": "male",
                "lname": "Doe",
                "fname": "John",
                "sname": "Smith",
                "param1": "custom1",
                "param2": "custom2",
                "param3": "custom3",
                "operator": 5,
                "extendOperator": "BEELINE",
            },
        )
        mock_request.assert_called_once_with(
            "contact/add",
            {
                "number": number,
                "groupId": group_id,
                "birthday": birthday,
                "sex": sex,
                "lname": last_name,
                "fname": first_name,
                "sname": surname,
                "param1": param1,
                "param2": param2,
                "param3": param3,
            },
        )

    @patch.object(SmsAero, "request")
    async def test_contact_list(self, mock_request):
        mock_request.return_value = {
            "0": {
                "id": "12345",
                "number": "79031234567",
                "sex": "male",
                "lname": "Doe",
                "fname": "John",
                "sname": "Smith",
                "param1": "custom1",
                "param2": "custom2",
                "param3": "custom3",
                "operator": 5,
                "extendOperator": "BEELINE",
            },
            "links": {
                "self": "/v2/contact/list?page=1",
                "first": "/v2/contact/list?page=1",
                "last": "/v2/contact/list?page=1",
            },
            "totalCount": "1",
        }
        number = 79031234567
        group_id = 6789
        birthday = "1990-01-01"
        sex = "male"
        operator = "BEELINE"
        last_name = "Doe"
        first_name = "John"
        surname = "Smith"
        page = 1

        result = await self.smsaero.contact_list(
            number=number,
            group_id=group_id,
            birthday=birthday,
            sex=sex,
            operator=operator,
            last_name=last_name,
            first_name=first_name,
            surname=surname,
            page=page,
        )

        self.assertEqual(
            result,
            {
                "0": {
                    "id": "12345",
                    "number": "79031234567",
                    "sex": "male",
                    "lname": "Doe",
                    "fname": "John",
                    "sname": "Smith",
                    "param1": "custom1",
                    "param2": "custom2",
                    "param3": "custom3",
                    "operator": 5,
                    "extendOperator": "BEELINE",
                },
                "links": {
                    "self": "/v2/contact/list?page=1",
                    "first": "/v2/contact/list?page=1",
                    "last": "/v2/contact/list?page=1",
                },
                "totalCount": "1",
            },
        )
        mock_request.assert_called_once_with(
            "contact/list",
            {
                "number": number,
                "groupId": group_id,
                "birthday": birthday,
                "sex": sex,
                "operator": operator,
                "lname": last_name,
                "fname": first_name,
                "sname": surname,
            },
            page,
        )

    @patch.object(SmsAero, "request")
    async def test_contact_delete(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.contact_delete(1)
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("contact/delete", {"id": 1})

    @patch.object(SmsAero, "request")
    async def test_contact_delete_all(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.contact_delete_all()
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("contact/delete-all")

    @patch.object(SmsAero, "request")
    async def test_blacklist_add(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.blacklist_add(79031234567)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("blacklist/add", {"number": 79031234567})

    @patch.object(SmsAero, "request")
    async def test_blacklist_list(self, mock_request):
        mock_request.return_value = {"success": True, "data": {}}
        page = 1
        result = await self.smsaero.blacklist_list(page=page)
        self.assertEqual(result, {"success": True, "data": {}})
        mock_request.assert_called_once_with("blacklist/list", None, page)

    @patch.object(SmsAero, "request")
    async def test_blacklist_delete(self, mock_request):
        mock_request.return_value = None
        result = await self.smsaero.blacklist_delete(1)
        self.assertEqual(result, True)
        mock_request.assert_called_once_with("blacklist/delete", {"id": 1})

    @patch.object(SmsAero, "request")
    async def test_hlr_check(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.hlr_check(79031234567)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("hlr/check", {"number": 79031234567})

    @patch.object(SmsAero, "request")
    async def test_hlr_status(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.hlr_status(1)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("hlr/status", {"id": 1})

    @patch.object(SmsAero, "request")
    async def test_number_operator(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.number_operator(79031234567)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("number/operator", {"number": 79031234567})

    def test_enable_test_mode(self):
        self.smsaero.enable_test_mode()
        self.assertTrue(self.smsaero.is_test_mode_active())

    def test_disable_test_mode(self):
        self.smsaero.disable_test_mode()
        self.assertFalse(self.smsaero.is_test_mode_active())

    @patch.object(SmsAero, "request")
    async def test_viber_statistics_with_sending_id(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.viber_statistics(sending_id=123)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("viber/statistic", {"sendingId": 123}, page=None)

    @patch.object(SmsAero, "request")
    async def test_viber_statistics_with_sending_id_and_page(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.viber_statistics(sending_id=123, page=2)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("viber/statistic", {"sendingId": 123}, page=2)

    @patch.object(SmsAero, "request")
    async def test_viber_list_without_parameters(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.viber_list()
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("viber/list", page=None)

    @patch.object(SmsAero, "request")
    async def test_viber_list_with_page(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.viber_list(page=2)
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("viber/list", page=2)

    @patch.object(SmsAero, "request")
    async def test_viber_sign_list(self, mock_request):
        mock_request.return_value = {"success": True}
        result = await self.smsaero.viber_sign_list()
        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with("viber/sign/list")

    @patch.object(SmsAero, "request")
    async def test_viber_send(self, mock_request):
        mock_request.return_value = {"success": True}

        result = await self.smsaero.viber_send(
            "test sign",
            "VIBER",
            "test message",
        )

        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with(
            "viber/send",
            {
                "groupId": None,
                "sign": "test sign",
                "channel": "VIBER",
                "text": "test message",
                "imageSource": None,
                "textButton": None,
                "linkButton": None,
                "dateSend": None,
                "signSms": None,
                "channelSms": None,
                "textSms": None,
                "priceSms": None,
            },
        )

    @patch.object(SmsAero, "request")
    async def test_viber_send_with_number(self, mock_request):
        mock_request.return_value = {"success": True}

        result = await self.smsaero.viber_send(
            "test sign",
            "VIBER",
            "test message",
            79031234567,
        )

        self.assertEqual(result, {"success": True})
        mock_request.assert_called_once_with(
            "viber/send",
            {
                "groupId": None,
                "sign": "test sign",
                "channel": "VIBER",
                "text": "test message",
                "imageSource": None,
                "textButton": None,
                "linkButton": None,
                "dateSend": None,
                "signSms": None,
                "channelSms": None,
                "textSms": None,
                "priceSms": None,
                "number": 79031234567,
            },
        )
