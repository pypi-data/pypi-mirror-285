import secrets, string


def license_key():
    return '-'.join(
        ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(secrets.randbelow(4) + 3)) for _ in
        range(6))[:-1]


print(license_key())


def license_key_v2(min_part_length=3, max_part_length=6, num_parts=6, separator='-', total_length=None,
                   total_separators=None):
    if total_separators is not None:
        num_parts = total_separators + 1

    # Generate the parts with random lengths
    parts = [
        ''.join(secrets.choice(string.ascii_letters + string.digits)
                for _ in range(secrets.randbelow(max_part_length - min_part_length + 1) + min_part_length))
        for _ in range(num_parts)
    ]

    # Join parts using the specified separator
    key = separator.join(parts)

    # If total_length is specified and greater than current length, add random characters
    if total_length is not None and len(key) < total_length:
        additional_chars = ''.join(secrets.choice(string.ascii_letters + string.digits)
                                   for _ in range(total_length - len(key)))
        key += additional_chars

    return key

"""
パラメータ
min_part_length (int): 各部分の最小長さを指定します。デフォルトは3です。
max_part_length (int): 各部分の最大長さを指定します。デフォルトは6です。
num_parts (int): ライセンスキーの部分の数を指定します。デフォルトは6です。
separator (str): 部分間のセパレーターを指定します。デフォルトは '-' です。
total_length (int): ライセンスキーの総文字数を指定します。デフォルトは None（指定なし）です。
total_separators (int): ライセンスキーのセパレーターの数を指定します。デフォルトは None（指定なし）です。このオプションを指定すると、num_parts は total_separators + 1 に設定されます。

戻り値
str: 生成されたライセンスキーを返します。
"""
print(license_key_v2())
print(license_key_v2(min_part_length=4, max_part_length=8, num_parts=4, separator='-', total_length=25))
print(license_key_v2(min_part_length=4, max_part_length=8, total_separators=3))
