from enum import Enum, auto


class DataLicense(Enum):
    # Creative Commons Licenses
    CC0 = auto()
    CC_BY = auto()
    CC_BY_SA = auto()
    CC_BY_NC = auto()
    CC_BY_NC_SA = auto()

    # Open Data Commons Licenses
    PDDL = auto()
    ODC_BY = auto()
    ODC_ODbL = auto()


if __name__ == "__main__":
    # Print all license names and values
    for lic in DataLicense:
        print(f'{lic.name}: {lic.value}')
