class LeanIXTechDiscoveryBaseException(Exception):
    """Base exception for tech discovery demo provisioner
    """
    pass


class LeanIXAPIAuthenticatorException(LeanIXTechDiscoveryBaseException):
    """Exception handler for tech discovery API authenticator
    """
    pass


class LeanIXDemoProvisionerException(LeanIXTechDiscoveryBaseException):
    """Exception handler for tech discovery demo provisioner
    """
    pass


class LeanIXDemoFactoryException(LeanIXTechDiscoveryBaseException):
    """Exception handler for tech discovery demo factory
    """
    pass
