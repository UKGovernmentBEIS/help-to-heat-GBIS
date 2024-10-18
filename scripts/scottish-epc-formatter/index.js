const csv = require('csv');
const { program } = require('commander');
const { readFileSync, writeFileSync, fstat } = require('fs');

program.option('--infile <string>', 'infile', 'input.csv');
program.option('--outfile <string>', 'outfile', undefined);

program.parse();

const options = program.opts();

const inFile = options.infile;
const outFile = options.outfile ?? options.infile;

const content = readFileSync(inFile);

const records = csv.parse(content, {columns: true, bom: true});

const mapping = new Map();
mapping.set("OSG_REFERENCE_NUMBER", "uprn");
mapping.set("CURRENT_ENERGY_RATING", "rating");
mapping.set("LODGEMENT_DATE", "date");
mapping.set("PROPERTY_TYPE", "property_type");
mapping.set("ADDRESS1", "address1");
mapping.set("ADDRESS2", "address2");
mapping.set("ADDRESS3", "address3");
mapping.set("POSTCODE", "postcode");
mapping.set("BUILDING_REFERENCE_NUMBER", "building_reference_number");
mapping.set("POTENTIAL_ENERGY_RATING", "potential_rating");
mapping.set("CURRENT_ENERGY_EFFICIENCY", "current_energy_efficiency_rating");
mapping.set("POTENTIAL_ENERGY_EFFICIENCY", "potential_energy_efficiency_rating");
mapping.set("BUILT_FORM", "built_form");
mapping.set("INSPECTION_DATE", "inspection_date");
mapping.set("LOCAL_AUTHORITY_LABEL", "local_authority");
mapping.set("CONSTITUENCY_LABEL", "constituency");
mapping.set("ENERGY_CONSUMPTION_CURRENT", "energy_consumption");
mapping.set("ENERGY_CONSUMPTION_POTENTIAL", "potential_energy_consumption");
mapping.set("CO2_EMISSIONS_CURRENT", "co2_emissions");
mapping.set("CO2_EMISS_CURR_PER_FLOOR_AREA", "co2_emissions_per_floor_area");
mapping.set("CO2_EMISSIONS_POTENTIAL", "co2_emissions_potential");
mapping.set("TOTAL_FLOOR_AREA", "floor_area");
mapping.set("FLOOR_LEVEL", "floor_level");
mapping.set("FLOOR_HEIGHT", "floor_height");
mapping.set("ENERGY_TARIFF", "energy_tariff");
mapping.set("MAINS_GAS_FLAG", "mains_gas");
mapping.set("MULTI_GLAZE_PROPORTION", "multiple_glazed_proportion");
mapping.set("EXTENSION_COUNT", "extension_count");
mapping.set("NUMBER_HABITABLE_ROOMS", "habitable_room_count");
mapping.set("NUMBER_HEATED_ROOMS", "heated_room_count");
mapping.set("FLOOR_DESCRIPTION", "floor_description");
mapping.set("FLOOR_ENERGY_EFF", "floor_energy_efficiency");
mapping.set("WINDOWS_DESCRIPTION", "windows_description");
mapping.set("WALL_DESCRIPTION", "wall_description");
mapping.set("WALL_ENERGY_EFF", "wall_energy_efficiency");
mapping.set("WALL_ENV_EFF", "wall_environmental_efficiency");
mapping.set("MAINHEAT_DESCRIPTION", "main_heating_description");
mapping.set("MAINHEAT_ENERGY_EFF", "main_heating_energy_efficiency");
mapping.set("MAINHEAT_ENV_EFF", "main_heating_environmental_efficiency");
mapping.set("MAIN_FUEL", "main_heating_fuel_type");
mapping.set("SECONDHEAT_DESCRIPTION", "second_heating_description");
mapping.set("SHEATING_ENERGY_EFF", "second_heating_energy_efficiency");
mapping.set("ROOF_DESCRIPTION", "roof_description");
mapping.set("ROOF_ENERGY_EFF", "roof_energy_efficiency");
mapping.set("ROOF_ENV_EFF", "roof_environmental_efficiency");
mapping.set("LIGHTING_DESCRIPTION", "lighting_description");
mapping.set("LIGHTING_ENERGY_EFF", "lighting_energy_efficiency");
mapping.set("LIGHTING_ENV_EFF", "lighting_environmental_efficiency");
mapping.set("MECHANICAL_VENTILATION", "mechanical_ventilation");
mapping.set("CONSTRUCTION_AGE_BAND", "construction_age_band");
mapping.set("TENURE", "tenure");
mapping.set("IMPROVEMENTS", "improvements");
mapping.set("ALTERNATIVE_IMPROVEMENTS", "alternative_improvements");

const outLines = [
    [...mapping.values()].join(",")
];

console.log(`start ${inFile} to ${outFile}`);

records.toArray().then(arr => {
    var i = 0;
    for (const epc of arr) {
        i++;
        if (i === 1) continue; // first line of the file is additional headers? ignore this

        const output_fields = [...mapping.keys()]
            .map(key => {
                if (epc[key] === undefined) {
                    console.log(key);
                    console.log(epc);
                    
                    throw new Error("undefined in data!");
                }

                return `"${epc[key]}"`;
            })

        outLines.push(output_fields.join(","));
    }

    writeFileSync(outFile, outLines.join("\n"));

    console.log(`finish ${inFile} to ${outFile}`);
});
