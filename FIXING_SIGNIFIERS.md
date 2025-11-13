# Fixing Signifier Files - Error Resolution Guide

## The Problem

The error you encountered:
```
Bad syntax (unterminated URI reference) at ^ in:
```

This error comes from **rdflib** (the RDF parser) and is caused by **two issues** in your signifier files:

1. **Invalid JSON syntax**: Single quotes (`'`) instead of double quotes (`"`)
2. **Invalid RDF comments**: Using `//` instead of `#`

## Root Cause

Your signifier files use a **non-standard RDF/Turtle syntax**:

```turtle
// This is NOT valid Turtle syntax  (should be #)
cashmere:hasStructuredDescription "
    {
        'intent': 'increase luminosity'   # Single quotes NOT valid JSON
    }
"^^xsd:string ;
```

### Issues:
- **Comments**: Turtle uses `#` for comments, not `//`
- **JSON strings**: JSON requires double quotes (`"`), not single quotes (`'`)
- **URI notation in JSON**: Using `<http://...>` inside JSON is non-standard (should be `"http://..."`)

## The Solution

### What Needs to Change

1. **Replace `//` comments with `#`**
2. **Use double quotes in JSON** (not single quotes)
3. **Quote URIs inside JSON** (use `"http://..."` not `<http://...>`)
4. **Add proper @prefix declarations**

### Corrected Example

Here's a properly formatted signifier file ([raise-blinds-signifier-fixed.ttl](signifiers/raise-blinds-signifier-fixed.ttl)):

```turtle
@prefix cashmere: <https://aimas.cs.pub.ro/ont/cashmere#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix hmas: <https://aimas.cs.pub.ro/ont/cashmere#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .

# Signifier for raising the blinds (use # for comments)

<#raise-blinds-signifier> a cashmere:Signifier ;
	cashmere:signifies <#adjust-blinds-action-affordance> ;
	cashmere:recommendsAbility [
    		a hmas:LLMReasoningAbility ;
	] ;
	cashmere:hasIntentionDescription [
    		a cashmere:IntentionDescription ;
    		cashmere:hasStructuredDescription """{
            		"intent": "increase luminosity in a room"
        		}"""^^xsd:string ;
	] ;
	cashmere:recommendsContext [
    	a cashmere:IntentContext ;
    	cashmere:hasStructuredDescription """{
            	"conditions": [
                	{
                    	"artifact": "http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308",
                    	"propertyAffordance": "http://example.org/LightSensor#hasLuminosityLevel",
                    	"valueConditions": [
                        	{
                            	"operator": "greaterThan",
                            	"value": 10000
                        	}
                    	]
                	},
                	{
                    	"artifact": "http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308",
                    	"propertyAffordance": "http://example.org/TemperatureSensor#hasTemperatureLevel",
                    	"valueConditions": [
                        	{
                            	"operator": "lessThan",
                            	"value": 25
                        	}
                    	]
                	}
            	]
        	}"""^^xsd:string ;

    		cashmere:hasShaclCondition [
        			a sh:NodeShape ;
        	    		sh:targetNode <http://example.org/precis/workspaces/lab308/artifacts/external_light_sensing308> ;
        	    		sh:targetClass <http://example.org/LightSensor> ;
        	    		sh:property [
                	sh:path <http://example.org/LightSensor#hasLuminosityLevel> ;
                	sh:datatype xsd:integer ;
                	sh:minInclusive 10000 ;
]
    		] ;
    	cashmere:hasShaclCondition [
        		a sh:NodeShape ;
        	    	sh:targetNode <http://example.org/precis/workspaces/lab308/artifacts/temperature_sensor308> ;
        	    	sh:targetClass <http://example.org/TemperatureSensor> ;
        	    	sh:property [
                		sh:path <http://example.org/TemperatureSensor#hasTemperatureLevel> ;
                		sh:datatype xsd:integer ;
                		sh:maxInclusive 25 ;
        	    	]
    	]
    	] .
```

### Key Changes Made

| Original | Corrected | Reason |
|----------|-----------|--------|
| `//` comments | `#` comments | Turtle standard |
| `'intent': 'text'` | `"intent": "text"` | Valid JSON |
| `<http://...>` in JSON | `"http://..."` | Valid JSON |
| No @prefix declarations | Added @prefix lines | Required for Turtle |
| `sh:dataType` | `sh:datatype` | Correct SHACL property name |

## How to Fix Your Files

### Option 1: Manual Editing

Edit each `.txt` file in the `signifiers/` directory:

1. Add @prefix declarations at the top
2. Change `//` to `#`
3. In JSON sections, change:
   - `'key'` → `"key"`
   - `'value'` → `"value"`
   - `<http://example.org/...>` → `"http://example.org/..."`

### Option 2: Use the Fix Script (Automated)

A script has been created but needs refinement. For now, **manual editing is recommended**.

## Testing Your Fixed Files

Once you've corrected a file, test it:

```bash
python -c "
from src.storage.registry import SignifierRegistry
registry = SignifierRegistry()

with open('signifiers/your-file-fixed.ttl', 'r') as f:
    rdf_data = f.read()

signifier = registry.create_from_rdf(rdf_data)
print(f'Success! Loaded: {signifier.signifier_id}')
"
```

## Summary

**The Error Source**: rdflib RDF parser
**The Cause**: Non-standard Turtle syntax (// comments, single-quoted JSON)
**The Fix**: Use standard Turtle (#comments, double-quoted JSON, @prefix declarations)
**Example**: See [raise-blinds-signifier-fixed.ttl](signifiers/raise-blinds-signifier-fixed.ttl)

After fixing your signifier files, they will load successfully into the RD4 system!
