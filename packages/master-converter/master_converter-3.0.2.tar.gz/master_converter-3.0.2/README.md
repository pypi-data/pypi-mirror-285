A Package for converting between a lot of units

**Installing**

To install just run the following command:

```
pip install master-converter
```

**Code Examples**

```
from master_converter import Length, Mass

meters = Length.Inches(3).Inches_Meters()
print(meters)

long_tons = Mass.Milligrams(3).Milligrams_Long_Tons()
print(long_tons)
```

Please don't hesitate to send me feedback by emailing me at master_converter@protonmail.com
