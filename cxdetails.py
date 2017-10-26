# Import PyCheckMarx
import PyCheckmarx
import json
import stashy
import argparse

pyC = PyCheckmarx.PyCheckmarx()

print pyC.getSupressedIssues(1000232)
