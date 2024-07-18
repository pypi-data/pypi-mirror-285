from pydantic import Extra, HttpUrl, EmailStr
from typing import Tuple, List, Optional
from redis_om import JsonModel, Field
from datetime import date


### Models for Kiwi

class Product(JsonModel):
    product_id: str = Field(..., description="Unique identifier for the product", index=True)
    name: str = Field(..., description="Name of the product", index=True)
    description: str = Field(..., description="Description of the product")
    category: Optional[str] = Field(None, description="Category the product belongs to")
    price: Optional[float] = Field(None, description="Price of the product")
    currency: Optional[str] = Field(None, description="Currency for the price")
    stock_quantity: Optional[int] = Field(None, description="Number of items in stock")
    sku: Optional[str] = Field(None, description="Stock Keeping Unit identifier")
    manufacturer: Optional[str] = Field(None, description="Manufacturer of the product")
    warranty: Optional[str] = Field(None, description="Warranty period for the product")
    dimensions: Optional[List[str]] = Field([], description="Dimensions of the product (length, width, height)")
    weight: Optional[float] = Field(None, description="Weight of the product")
    color: Optional[str] = Field(None, description="Color of the product")
    release_date: Optional[date] = Field(None, description="Release date of the product")
    end_of_life_date: Optional[date] = Field(None, description="End of life date of the product")
    download_url: Optional[HttpUrl] = Field(None, description="URL to download the product, if applicable")
    documentation_url: Optional[HttpUrl] = Field(None, description="URL to the documentation, if applicable")
    features: Optional[List[Tuple[str, str]]] = []

    def get_summary(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk' and type(v)!=list})

    def __str__(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk' and type(v)!=list})

    def get_long_description(self):
        summary = self.get_summary()
        features = "\nFEATURES: \n"+"\n".join(f"{k} : {v}" for k,v in self.features) if self.features else ""
        return summary+features

class Service(JsonModel):
    service_id: str = Field(..., description="Unique identifier for the service", index=True)
    name: str = Field(..., description="Name of the service", index=True)
    description: str = Field(..., description="Description of the service")
    category: Optional[str] = Field(None, description="Category the service belongs to")
    price: Optional[float] = Field(None, description="Price of the service")
    currency: Optional[str] = Field(None, description="Currency for the price")
    availability: Optional[str] = Field(None, description="Availability status of the service")
    provider: Optional[str] = Field(None, description="Provider of the service")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for the service provider")
    contact_phone: Optional[str] = Field(None, description="Contact phone number for the service provider")
    website: Optional[HttpUrl] = Field(None, description="Website URL for the service")
    service_area: Optional[str] = Field(None, description="Geographical area where the service is offered")
    service_start_date: Optional[date] = Field(None, description="Start date of the service availability")
    service_end_date: Optional[date] = Field(None, description="End date of the service availability")
    features: Optional[List[Tuple[str, str]]] = []

    def get_long_description(self):
        summary = self.get_summary()
        features = "\nFEATURES: \n"+"\n".join(f"{k} : {v}" for k,v in self.features) if self.features else ""
        return summary+features
    
    def get_summary(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk' and type(v)!=list})
        
    def __str__(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk' and type(v)!=list})

class Company(JsonModel, extra=Extra.allow):
    name: str = Field(..., description="Name of the company", index=True)
    vision: Optional[str] = Field(None, description="Vision of the company")
    mission: Optional[str] = Field(None, description="Mission of the company")  

    description: Optional[str] = Field(None, description="Description of the company")

    company_culture: Optional[str] = Field(None, description="company culture")
    
    values: Optional[List[Tuple[str, str]]] = Field(None, description="company values")
    industry: Optional[str] = Field(None, description="Industry the company operates in")
    founded: Optional[int|None] = Field(None, description="Year the company was founded")
    num_employees: Optional[int|None] = Field(None, description="Number of employees in the company")
    headquarters: Optional[str] = Field(None, description="Location of the company's headquarters")
    website: Optional[HttpUrl] = Field(None, description="Website URL of the company")
    email: Optional[EmailStr] = Field(None, description="Contact email of the company")
    phone: Optional[str] = Field(None, description="Contact phone number of the company")
    address: Optional[str] = Field(None, description="Physical address of the company")
    social_media: Optional[dict] = Field(None, description="Social media links of the company")

    products: Optional[List[str]] = Field(None, description="List of references to products offered by the company")
    services: Optional[List[str]] = Field(None, description="List of references to services offered by the company")


    def get_contact_info(self) -> str:
        contact_info = f"Email: {self.email}, Phone: {self.phone}, Website: {self.website}"
        return contact_info

    def get_summary(self) -> str:
        summary = [
            f"Company Name: {self.name}\n",
            f"Industry: {self.industry}\n",
            f"Founded: {self.founded}\n",
            f"Number of Employees: {self.num_employees}\n",
            f"Headquarters: {self.headquarters}\n",
            f"Website: {self.website}\n",
            f"Description: {self.description}\n",
        ]
        summary = [i for i in summary if 'None' not in i]
        return "".join(summary)

    
    def get_description(self) -> str:
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k not in ('pk', 'products', 'services')})

    def get_long_description(self) -> str:
        products_descriptions, services_descriptions = "", ""
        products = [Product.find(Product.pk==p).first() for p in self.products]
        services = [Service.find(Service.pk==s).first() for s in self.services]
        if products:
            products_descriptions = "\nPRODUCTS:\n"+"\n".join(p.get_long_description() for p in products)
        if services:
            services_descriptions = "\nSERVICES\n"+"\n".join(s.get_long_description() for s in services)
            
        return self.get_description()+products_descriptions+services_descriptions

    
        
    def __str__(self):
        return '\n'.join({f"{k.upper()} : {v}" for k,v in self.dict().items() if v and k!='pk'})


