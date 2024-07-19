from dataclasses import dataclass, field
from typing import List, Optional
from dacite import from_dict
import json

@dataclass
class Summary:
    generatedon: str
    parser: str
    assemblies: int
    classes: int
    files: int
    coveredlines: int
    uncoveredlines: int
    coverablelines: int
    totallines: int
    linecoverage: Optional[float]
    coveredbranches: int
    totalbranches: int
    branchcoverage: Optional[float]
    coveredmethods: int
    totalmethods: int
    methodcoverage: Optional[float]

@dataclass
class Class:
    name: str
    coverage: Optional[float]
    coveredlines: int
    coverablelines: int
    totallines: int
    branchcoverage: Optional[float]
    coveredbranches: int
    totalbranches: int
    methodcoverage: Optional[float]
    coveredmethods: int
    totalmethods: int

@dataclass
class Assembly:
    name: str
    classes: int
    coverage: Optional[float]
    coveredlines: int
    coverablelines: int
    totallines: int
    branchcoverage: Optional[float]
    coveredbranches: int
    totalbranches: int
    methodcoverage: Optional[float]
    coveredmethods: int
    totalmethods: int
    classesinassembly: List[Class] = field(default_factory=list)

@dataclass
class Coverage:
    assemblies: List[Assembly] = field(default_factory=list)

@dataclass
class CoverageData:
    summary: Summary
    coverage: Coverage

def map_json_to_model(json_data: str) -> CoverageData:
    data = json.loads(json_data)
    return from_dict(data_class=CoverageData, data=data)