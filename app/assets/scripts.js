window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        update_graph: function(diameter_type, display_nodes, min_fraction_slider, max_regulations_slider, graph_data, compare_switch, selection_data) {

			if(Object.keys(graph_data).length != 0){
				
				var data = JSON.parse(JSON.stringify(graph_data))
				var layout = {"name": "klay"};
				var display = new Set();
				var compare = "compare" in data;

				if (display_nodes !== 'a'){
					
					if(selection_data["gene_ids"].length == 1){
						layout = {'name': 'concentric'};
					}
					else{
						layout = {'name': 'klay'};
					}
					display.add(display_nodes)
				}
				else{
					display.add("s");
					display.add("t");
				}

				var diameter = 30;
				var elements = [];
				
				for (var gene of data["center"]){
				    diameter = 30;
					if (diameter_type === "me"){
					    if(gene["data"]["methylation"] !== null){
					    	diameter = 10 + gene["data"]["methylation"] * 90;
					    }
					    else{
					        gene["classes"] = gene["classes"] + " no_data";
					    }
					}
					else if (diameter_type === "mu"){
					    diameter = Math.min(10 + gene["data"]["mutation"] * 200, 100);
					}
					gene["data"]["diameter"] = diameter;

					elements.push(gene);
				}
				
				var nr = 0;
				var target_counter = 0;
				var source_counter = 0;
				
				for (var regulation of data["regulations"]){
					
					if(nr >= max_regulations_slider){break;}
					
					var gene = regulation[1];
					var reg = regulation[0];
					
					if(reg["data"]["fraction"] < min_fraction_slider){break;}

					if(!compare){

					    reg["data"]["colors"] = "red red grey grey";
					    reg["data"]["divide"] = "0% "+ reg["data"]["fraction"]*100+"% " + reg["data"]["fraction"]*100 + "% 100%";
					    reg["data"]["diff"] = 0;

					} else{

					    var diff = data["compare"][reg["data"]["regulation_id"]] - reg["data"]["fraction"];

                        if(compare_switch){

                            if (diff > 0){
                                reg["data"]["colors"] = "green green grey grey";
                                reg["data"]["divide"] = "0% "+ diff*100+"% " + diff*100 + "% 100%";
                            } else {
                                reg["data"]["colors"] = "orange orange grey grey";
                                reg["data"]["divide"] = "0% "+ diff*-100+"% " + diff*-100 + "% 100%";
                            }
                            reg["data"]["weight"] = Math.abs(diff)*10+3;

                        }else{
                        	 reg["data"]["colors"] = "red red grey grey";
					         reg["data"]["divide"] = "0% "+ reg["data"]["fraction"]*100+"% " + reg["data"]["fraction"]*100 + "% 100%";
                        }


                        reg["data"]["diff"] = diff * -1;


					}
					
					if(Object.keys(gene).length === 0){
						nr += 1;
						target_counter += 1;
						source_counter += 1;
						elements.push(reg);
					}
					else if( display.has(gene["classes"]) ){
                        diameter = 30;
                        if(gene["classes"] === "t"){
						    target_counter+=1;
						}
						else if (gene["classes"] === "s"){
						    source_counter += 1;
						}
						nr += 1;

                        if (diameter_type === "me"){
                            if(gene["data"]["methylation"] !== null){
                                diameter = 10 + gene["data"]["methylation"] * 90;
                            }
                            else{
                                gene["classes"] = gene["classes"] + " no_data";
                            }

                        }
                        else if (diameter_type === "mu"){
                            diameter = Math.min(10 + gene["data"]["mutation"] * 200, 100);
                        }
						gene["data"]["diameter"] = diameter;

						elements.push(gene);
						elements.push(reg);
					}
				}

				return [elements, layout, target_counter, source_counter, compare];
			}
			else{
				return [[], {"name": "klay"}, 0, 0]
			}
        },

		update_user_graph: function(display_nodes, min_fraction_slider, max_regulations_slider, graph_data, genes) {
			if(Object.keys(graph_data).length != 0){
				
				var data = JSON.parse(JSON.stringify(graph_data))
				var layout = {"name": "klay"};
				var display = new Set();

				if (display_nodes !== 'a'){
					
					if(genes.length == 1){
						layout = {'name': 'concentric'};
					}
					else{
						layout = {'name': 'klay'};
					}
					display.add(display_nodes)
				}
				else{
					display.add("s");
					display.add("t");
				}

				var diameter = 30;
				var elements = [];
				
				for (var gene of data["center"]){
				    diameter = 30;
					gene["data"]["diameter"] = diameter;

					elements.push(gene);
				}
				
				var nr = 0;
				var target_counter = 0;
				var source_counter = 0;
			
				for (var regulation of data["regulations"]){
									
					
					if(nr >= max_regulations_slider){break;}

					var gene = regulation[1];
					var reg = regulation[0];

					if(reg["data"]["fraction"] < min_fraction_slider){continue;}

					
					reg["data"]["colors"] = "red red grey grey";
					reg["data"]["divide"] = "0% "+ reg["data"]["fraction"]*100+"% " + reg["data"]["fraction"]*100 + "% 100%";
					reg["data"]["diff"] = 0;
						
					if(Object.keys(gene).length === 0){
						nr += 1;
						target_counter += 1;
						source_counter += 1;
						elements.push(reg);
					}
					else if( display.has(gene["classes"]) ){
                        diameter = 30;
                        if(gene["classes"] === "t"){
						    target_counter+=1;
						}
						else if (gene["classes"] === "s"){
						    source_counter += 1;
						}
						nr += 1;

						gene["data"]["diameter"] = diameter;
						elements.push(gene);
						elements.push(reg);
					}
				}
				return [elements, layout, target_counter, source_counter];
			}
			else{
				return [[], {"name": "klay"}, 0, 0]
			}
        }

    }
});