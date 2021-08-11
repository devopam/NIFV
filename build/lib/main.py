import re
from dataclasses import dataclass
from stdnum import luhn
from stdnum import verhoeff


@dataclass
class ValidationResponse:
    """
    Class object that contains a validation response structure ( message , status and is_valid flag )
    Message gives additional information on either the error or the valid output
    Status is an integer value that does sub-classification of the error if any. 0 for success
    is_valid is a boolean flag that gives True for success
    Please note it doesn't actually verify online with the Government information and only checks the formats
    """
    message: str
    status: int
    is_valid: bool


class NationalIdentifierFormatValidator:
    """
        Utility class for format validation of various National Identifiers viz.
        a. PAN (India)
        b. Aadhaar (India)
        c. SSN (USA)
        d. CPF (Brazil)
        e. CNPJ (Brazil)
        f. NPWP (Indonesia)
        g. NI (UK)
        The methods return standard format of the identifier if it is considered valid else None
    """
    _message_: str
    _status_: int
    _is_valid_: bool
    _valid_fourth_char_PAN_ = []
    _PAN_length_: int

    def __init__(self):
        self._message_ = ""
        self._status_ = 0
        self._is_valid_ = False
        self._PAN_length_ = 10
        self._valid_fourth_char_PAN_ = ['A', 'B', 'C', 'F', 'G', 'H', 'L', 'J', 'P', 'T']

    def validate_PAN(self, pan_number: str = ""):
        """
        Method to validate India tax identifier PAN ( Permanent Account Number ) .

        :param pan_number: Input PAN number string . Can accept space, dash, dot and slash
        :return: ValidationResponse object: message with error details or formatted PAN number;
                 status with the code ( 0 for success, -1 for incorrect length, -2 for invalid fourth character,
                 -3 for invalid digit pattern, -4 for invalid pattern and -5 for non-alnum chars;
                 is_valid boolean flag to simply indicate if it was a validation success.
        """
        pan_number = pan_number.translate({ord(ch): '' for ch in " -./"}).strip().upper()
        regex_pattern = "[A-Z]{5}[0-9]{4}[A-Z]{1}"

        if len(pan_number) != self._PAN_length_:
            self._message_ = "A Valid Indian PAN number is 10 characters wide"
            self._status_ = -1
            self._is_valid_ = False
        elif pan_number.isalnum():
            p = re.compile(regex_pattern)
            if re.search(p, pan_number):
                if 1 <= int(pan_number[5:9]) <= 9999:
                    if pan_number[3] in self._valid_fourth_char_PAN_:
                        self._message_ = pan_number
                        self._status_ = 0
                        self._is_valid_ = True
                    else:
                        self._message_ = "Invalid Fourth Character detected in PAN"
                        self._status_ = -2
                        self._is_valid_ = False
                else:
                    self._message_ = "Invalid digit pattern detected in PAN"
                    self._status_ = -3
                    self._is_valid_ = False
            else:
                self._message_ = "Invalid pattern detected in PAN"
                self._status_ = -4
                self._is_valid_ = False
        else:
            self._message_ = "Input PAN doesn't conform to Indian PAN standards. Contains special chars"
            self._status_ = -5
            self._is_valid_ = False
        return ValidationResponse(self._message_, self._status_, self._is_valid_)

    def validate_PAN_lite(self, pan_number=""):
        """
        Method to validate PAN. Exact format failure reason is not provided.
        :param pan_number: str: Input PAN number string . Can accept space, dash, dot and slash
        :return: str: formatted PAN number if it is found valid else None
        """
        pan_number = pan_number.translate({ord(ch): '' for ch in " -./"}).strip().upper()
        regex_pattern = "[A-Z]{5}[0-9]{4}[A-Z]{1}"
        p = re.compile(regex_pattern)

        if len(pan_number) == self._PAN_length_ \
                and pan_number.isalnum() \
                and pan_number[3] in self._valid_fourth_char_PAN_ \
                and 1 <= int(pan_number[5:9]) <= 9999 \
                and re.search(p, pan_number):
            return pan_number
        else:
            return None

    def validate_PAN_with_name(self, pan_number="", name=""):
        """
        Method validates PAN format with name check of the registered entity
        :param pan_number: string with PAN number
        :param name: Registered Name of the entity as per PAN
        :return: ValdiationResponse object with formatted PAN number/Error description, status code and boolean check flag
        """
        pan_number = pan_number.translate({ord(ch): '' for ch in " -./"}).strip().upper()
        self._is_valid_ = True
        if len(name.strip()) == 0:
            self._message_ = "Please provide registered name of of the entity"
            self._status_ = -1
            self._is_valid_ = False
        elif pan_number[3] == "P":
            if len(name.strip().split(" ")) < 2:
                self._message_ = "Please provide last name of of the entity"
                self._status_ = -2
                self._is_valid_ = False
            elif name.strip().split(" ")[-1][0].upper() != pan_number[4]:
                self._message_ = "Mismatch in last name and PAN detected for individual entity"
                self._status_ = -3
                self._is_valid_ = False
        elif name.strip().split(" ")[0][0].upper() != pan_number[4]:
            self._message_ = "Mismatch in first name and PAN detected for non-individual entity"
            self._status_ = -4
            self._is_valid_ = False

        if self._is_valid_ is True:
            return self.validate_PAN(pan_number)
        else:
            return ValidationResponse(self._message_, self._status_, self._is_valid_)

    def validate_PAN_with_name_lite(self, pan_number="", name=""):
        """
        Method validates PAN format with name check of the registered entity
        :param pan_number: string with PAN number
        :param name: Registered Name of the entity as per PAN
        :return: formatted PAN number if found valid else None
        """
        pan_number = pan_number.translate({ord(ch): '' for ch in " -./"}).strip()
        name = name.strip().upper()
        is_valid = False
        if len(pan_number) > 0 and len(name) > 0:
            if (pan_number[3] == "P" and name.split(" ")[-1][0] == pan_number[4]) or pan_number[3] != "P" and \
                    name.split(" ")[0][0] == pan_number[4]:
                is_valid = True

        if is_valid is True:
            return self.validate_PAN_lite(pan_number)
        else:
            return None

    def validate_National_Insurance_Number(self, national_insurance_number=""):
        """
        Method to validate NI UK
        :param national_insurance_number: string. May contain space dash dot slash.
        :return: formatted National Insurance number if valid else None
        """
        regex_pattern = "(?!BG)(?!GB)(?!NK)(?!KN)(?!TN)(?!NT)(?!ZZ)(?:[A-CEGHJ-PR-TW-Z][A-CEGHJ-NPR-TW-Z]){6}([A-D]{1})"
        unallocated_begin_sequence = ["BG", "GB", "NK", "KN", "TN", "NT", "ZZ"]
        invalid_first_char = ['D', 'F', 'I', 'Q', 'U', 'V']
        invalid_second_char = ['D', 'F', 'I', 'O', 'Q', 'U', 'V']
        allowed_last_char = ['A', 'B', 'C', 'D', ' ']
        national_insurance_number = national_insurance_number.translate({ord(ch): '' for ch in " -./"}).strip()
        last_char = national_insurance_number[-1] if (len(national_insurance_number) == 9) else " "
        if len(national_insurance_number) < 8 or \
                national_insurance_number[:2] in unallocated_begin_sequence or \
                national_insurance_number[0] in invalid_first_char or \
                national_insurance_number[1] in invalid_second_char or \
                (national_insurance_number[3:8].isnumeric() is False) or \
                last_char not in allowed_last_char:
            return None
        else:
            return national_insurance_number

    def validate_SSN(self, social_security_number=""):
        """
        Method to validate Social Security Number of USA
        :param social_security_number: string may contain space dash dot slash
        :return: formatted social security number if valid else None
        """
        social_security_number = social_security_number.translate({ord(ch): '' for ch in " -./"}).strip()
        regex_pattern = "(?!000|666)[0-8][0-9]{2}(?!00)[0-9]{2}(?!0000)[0-9]{4}"
        p = re.compile(regex_pattern)
        if re.match(p, social_security_number):
            return social_security_number[:3] + "-" + social_security_number[3:5] + "-" + social_security_number[5:9]
        else:
            return None

    def validate_Aadhaar(self, aadhaar_number=""):
        """
        Method to validate Aadhaar number issued by UIDAI of India
        :param aadhaar_number: string may contain space dash dot slash
        :return: formatted full Aadhaar number if valid else None
        """
        aadhaar_number = aadhaar_number.translate({ord(ch): '' for ch in " -./"}).strip()
        if len(aadhaar_number) != 12 or aadhaar_number.isnumeric() is not True or \
                int(aadhaar_number[0]) < 2 or \
                verhoeff.is_valid(number=int(aadhaar_number)) is not True:
            return None
        else:
            return aadhaar_number[:4] + " " + aadhaar_number[4:8] + " " + aadhaar_number[8:12]

    def validate_NPWP(self, npwp_number=""):
        """
        Method to validate NPWP ( Nomor Pokok Wajib Pajak ) number of Indonesia
        :param npwp_number: may contain space dash dot slash
        :return: formatted NPWP number if valid else None
        """
        npwp_number = npwp_number.translate({ord(ch): '' for ch in " -./"}).strip()
        if len(npwp_number) != 15 or npwp_number.isdigit() is not True or luhn.is_valid(npwp_number[:9]) is not True:
            return None
        else:
            return '%s.%s.%s.%s-%s.%s' % (npwp_number[:2], npwp_number[2:5], npwp_number[5:8], npwp_number[8],
                                          npwp_number[9:12], npwp_number[12:])

    def cpf_calc_check_digits(self, cpf_number):
        """Calculate the check digits for the CPF number."""
        d1 = sum((10 - i) * int(cpf_number[i]) for i in range(9))
        d1 = (11 - d1) % 11 % 10
        d2 = sum((11 - i) * int(cpf_number[i]) for i in range(9)) + 2 * d1
        d2 = (11 - d2) % 11 % 10
        return '%d%d' % (d1, d2)

    def validate_CPF(self, cpf_number=""):
        """
        Method to validate CPF (Cadastro de Pessoas Físicas) number of Brazil
        :param cpf_number: string may contain space dash dot slash
        :return: formatted CPF number if valid else None
        """
        cpf_number = cpf_number.translate({ord(ch): '' for ch in " -./"}).strip()

        if len(cpf_number) != 11 or cpf_number.isdigit() is not True or int(cpf_number) <= 0 or \
                self.cpf_calc_check_digits(cpf_number) != cpf_number[-2:]:
            return None
        else:
            return cpf_number[:3] + '.' + cpf_number[3:6] + '.' + cpf_number[6:-2] + '-' + cpf_number[-2:]

    def cnpj_calc_check_digits(self, cnpj_number):
        """Calculate the check digits for the CNPJ number."""
        d1 = (11 - sum(((3 - i) % 8 + 2) * int(n)
                       for i, n in enumerate(cnpj_number[:12]))) % 11 % 10
        d2 = (11 - sum(((4 - i) % 8 + 2) * int(n)
                       for i, n in enumerate(cnpj_number[:12])) -
              2 * d1) % 11 % 10
        return '%d%d' % (d1, d2)

    def validate_CNPJ(self, cnpj_number=""):
        """
        Method to validate CNPJ (Cadastro Nacional da Pessoa Jurídica) number of Brazil
        :param cnpj_number: string may contain space dash dot slash
        :return: formatted CNPJ number if valid else None
        """
        cnpj_number = cnpj_number.translate({ord(ch): '' for ch in " -./"}).strip()
        if len(cnpj_number) != 14 or cnpj_number.isdigit() is not True or int(cnpj_number) <= 0 or \
                self.cnpj_calc_check_digits(cnpj_number) != cnpj_number[-2:]:
            return None
        else:
            return (cnpj_number[0:2] + '.' + cnpj_number[2:5] + '.' + cnpj_number[5:8] + '/' +
                    cnpj_number[8:12] + '-' + cnpj_number[12:]
                    )


if __name__ == '__main__':
    nifv = NationalIdentifierFormatValidator()
    print(nifv.validate_PAN("ABCP M0 00    1N"))
    print(nifv.validate_PAN_lite("ABCP M0 00    1N"))
    print(nifv.validate_PAN_with_name("AHHCM8632N", "Mevopam Dittra"))
    print(nifv.validate_PAN_with_name_lite("AHHCM8632N", "Mevopam Dittra"))
    print(nifv.validate_National_Insurance_Number("AA 11 22 33 D"))
    print(nifv.validate_SSN("625-47-3316"))
    print(nifv.validate_Aadhaar('8284 0242-15  50'))
    print(nifv.validate_NPWP("013000666091000"))
    print(nifv.validate_CPF("390  533  44705   "))
    print(nifv.validate_CNPJ("16.   727.230/0001-97  "))
