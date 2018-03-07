import hashlib

class Encrypt:

    #This generates CK-A, the ciphering key used for encryped communication
    #Call using Encrypt.a8(random,secret key)
    @staticmethod
    def a8(rand,K_A):
        return hashlib.sha256(int(str(rand) + str(K_A))).hexdigest()

    #This is used for authentication.
    @staticmethod
    def a3(rand,K_A):
        return hashlib.sha1(int(str(rand) + str(K_A))).hexdigest()