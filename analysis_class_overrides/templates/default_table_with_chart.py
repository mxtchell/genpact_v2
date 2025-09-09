default_table_with_chart_layout = """
{
	"layoutJson": {
		"type": "Document",
		"rows": 90,
		"columns": 160,
		"rowHeight": "1.11%",
		"colWidth": "0.625%",
		"gap": "0px",
		"style": {
			"backgroundColor": "#ffffff",
			"width": "100%",
			"height": "max-content",
			"padding": "15px",
			"gap": "20px"
		},
		"children": [
			{
				"name": "CardContainer0",
				"type": "CardContainer",
				"children": "",
				"minHeight": "80px",
				"rows": 2,
				"columns": 1,
				"style": {
					"border-radius": "11.911px",
					"background": "#2563EB",
					"padding": "10px",
					"fontFamily": "Arial"
				},
				"hidden": false
			},
			{
				"name": "Header0",
				"type": "Header",
				"children": "",
				"text": "Breakout Analysis - Total",
				"style": {
					"fontSize": "20px",
					"fontWeight": "700",
					"color": "#ffffff",
					"textAlign": "left",
					"alignItems": "center"
				},
				"parentId": "CardContainer0",
				"hidden": false
			},
			{
				"name": "Paragraph0",
				"type": "Paragraph",
				"children": "",
				"text": "Sales | Jan 2022-Mar 2023 | By Brand and Segment",
				"style": {
					"fontSize": "15px",
					"fontWeight": "normal",
					"textAlign": "center",
					"verticalAlign": "start",
					"color": "#fafafa",
					"border": "null",
					"textDecoration": "null",
					"writingMode": "horizontal-tb",
					"alignItems": "center"
				},
				"parentId": "CardContainer0",
				"hidden": false
			},
			{
				"name": "Header1",
				"type": "Header",
				"children": "",
				"text": "Analysis Summary",
				"style": {
					"fontSize": "20px",
					"fontWeight": "700",
					"textAlign": "left",
					"verticalAlign": "start",
					"color": "#000000",
					"backgroundColor": "#ffffff",
					"border": "null",
					"textDecoration": "null",
					"writingMode": "horizontal-tb",
					"borderBottom": "solid #DDD 2px"
				},
				"parentId": "CardContainer1",
				"flex": "",
				"hidden": false
			},
			{
				"name": "Markdown0",
				"type": "Markdown",
				"children": "",
				"text": "insights",
				"style": {
					"color": "#555",
					"backgroundColor": "#ffffff",
					"border": "null",
					"fontSize": "15px"
				},
				"parentId": "CardContainer1",
				"flex": "",
				"hidden": false
			},
			{
				"name": "CardContainer2",
				"type": "CardContainer",
				"children": "",
				"minHeight": "40px",
				"rows": 1,
				"columns": 34,
				"maxHeight": "40px",
				"style": {
					"borderRadius": "6.197px",
					"background": "var(--Blue-50, #EFF6FF)",
					"padding": "10px",
					"paddingLeft": "20px",
					"paddingRight": "20px"
				},
				"hidden": false
			},
			{
				"name": "Header2",
				"type": "Header",
				"width": 32,
				"children": "",
				"text": "<span style='font-family: Arial; margin-left: 5px;'>Growth is not available for the complete analysis period. This might impact the results</span>",
				"style": {
					"fontSize": "14px",
					"fontWeight": "normal",
					"textAlign": "left",
					"verticalAlign": "start",
					"color": "#1D4ED8",
					"border": "null",
					"textDecoration": "null",
					"writingMode": "horizontal-tb",
					"alignItems": "start",
					"fontFamily": ""
				},
				"parentId": "CardContainer2",
				"hidden": false
			},
			{
				"name": "FlexContainer5",
				"type": "FlexContainer",
				"minHeight": "250px",
				"direction": "row",
				"style": {
					"maxWidth": "90%",
					"width": "90%"
				}
			},
			{
				"name": "FlexContainer4",
				"type": "FlexContainer",
				"children": "",
				"minHeight": "250px",
				"direction": "column",
				"maxHeight": "1200px"
			},
			{
				"name": "Paragraph1",
				"type": "Paragraph",
				"children": "",
				"text": "* footnote for share calc",
				"style": {
					"fontSize": "12px",
					"fontWeight": "normal",
					"textAlign": "left",
					"verticalAlign": "start",
					"color": "#000000",
					"border": "null",
					"textDecoration": "null",
					"writingMode": "horizontal-tb"
				},
				"maxHeight": "32"
			},
			{
				"name": "CardContainer1",
				"type": "FlexContainer",
				"children": "",
				"direction": "column",
				"minHeight": "",
				"maxHeight": "",
				"style": {
					"borderRadius": "11.911px",
					"background": "var(--White, #FFF)",
					"box-shadow": "0px 0px 8.785px 0px rgba(0, 0, 0, 0.10) inset",
					"padding": "10px",
					"fontFamily": "Arial"
				},
				"flexDirection": "row",
				"hidden": false
			},
			{
				"name": "DataTable0",
				"type": "DataTable",
				"children": "",
				"columns": [
					{
						"name": "Column 1"
					},
					{
						"name": "Column 2"
					},
					{
						"name": "Column 3"
					},
					{
						"name": "Column 4"
					}
				],
				"data": [
					[
						"Row 1",
						0,
						0,
						0
					],
					[
						"Row 2",
						10,
						10,
						10
					],
					[
						"Row 3",
						20,
						20,
						20
					],
					[
						"Row 4",
						30,
						30,
						30
					],
					[
						"Row 5",
						40,
						40,
						40
					],
					[
						"Row 6",
						50,
						50,
						50
					],
					[
						"Row 7",
						60,
						60,
						60
					]
				],
				"parentId": "FlexContainer4",
				"caption": "",
				"styles": {
					"td": {
						"vertical-align": "middle"
					}
				}
			},
			{
				"name": "Markdown1",
				"type": "Markdown",
				"children": "",
				"text": "",
				"style": {
					"fontSize": "16px",
					"color": "#000000",
					"backgroundColor": "#ffffff",
					"border": "none"
				}
			},
			{
				"name": "HighchartsChart0",
				"type": "HighchartsChart",
				"minHeight": "400px",
				"chartOptions": {
					"chart": {
						"type": "bar"
					},
					"title": {
						"text": "Sample Highchart"
					},
					"xAxis": {
						"categories": [
							"Category A",
							"Category B",
							"Category C"
						]
					},
					"yAxis": {
						"title": {
							"text": "Values"
						}
					},
					"series": [
						{
							"name": "Series 1",
							"data": [
								10,
								20,
								30
							]
						}
					]
				},
				"options": {
					"chart": {
						"type": "bar",
						"polar": false
					},
					"title": {
						"text": "",
						"style": {
							"fontSize": "20px"
						}
					},
					"xAxis": {
						"categories": [
							"Category A",
							"Category B",
							"Category C"
						],
						"title": {
							"text": ""
						}
					},
					"yAxis": {
						"title": {
							"text": "Values"
						}
					},
					"series": [
						{
							"name": "Series 1",
							"data": [
								10,
								20,
								30
							]
						}
					],
					"credits": {
						"enabled": true
					},
					"legend": {
						"enabled": true,
						"align": "center",
						"verticalAlign": "bottom",
						"layout": "horizontal"
					},
					"plotOptions": {
						"column": {
							"dataLabels": {
								"style": {
									"fontSize": ""
								},
								"enabled": true
							}
						}
					}
				},
				"parentId": "FlexContainer5",
				"hidden": false
			}
		]
	},
	"inputVariables": [
		{
			"name": "exec_summary",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Markdown0",
					"fieldName": "text"
				}
			]
		},
		{
			"name": "hide_growth_warning",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "CardContainer2",
					"fieldName": "hidden"
				}
			]
		},
		{
			"name": "sub_headline",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Paragraph0",
					"fieldName": "text"
				}
			]
		},
		{
			"name": "headline",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Header0",
					"fieldName": "text"
				}
			]
		},
		{
			"name": "warning",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Header2",
					"fieldName": "text"
				}
			]
		},
		{
			"name": "data",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "DataTable0",
					"fieldName": "data"
				}
			]
		},
		{
			"name": "col_defs",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "DataTable0",
					"fieldName": "columns"
				}
			]
		},
		{
			"name": "footer",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Paragraph1",
					"fieldName": "text"
				}
			]
		},
		{
			"name": "hide_footer",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "Paragraph1",
					"fieldName": "hidden"
				}
			]
		},
		{
			"name": "chart_title",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "HighchartsChart0",
					"fieldName": "options.title.text"
				}
			]
		},
		{
			"name": "chart_categories",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "HighchartsChart0",
					"fieldName": "options.xAxis.categories"
				}
			]
		},
		{
			"name": "chart_y_axis",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "HighchartsChart0",
					"fieldName": "options.yAxis"
				}
			]
		},
		{
			"name": "chart_data",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "HighchartsChart0",
					"fieldName": "options.series"
				}
			]
		},
		{
			"name": "hide_chart",
			"isRequired": false,
			"defaultValue": null,
			"targets": [
				{
					"elementName": "FlexContainer5",
					"fieldName": "hidden"
				}
			]
		}
	]
}
"""