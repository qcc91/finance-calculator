#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 11:09:23 2024

@author: qinxiangyuan
"""

from sqlalchemy import and_

def data_conflict(table_name, filters):
    existing_record = table_name.query.filter(and_(*filters)).first()
    if existing_record:    
        return {'message': 'Data conflict. Please Check!'}
    else:
        return None
