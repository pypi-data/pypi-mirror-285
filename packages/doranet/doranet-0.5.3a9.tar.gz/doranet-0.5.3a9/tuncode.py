from datetime import datetime

from IPython.display import display

todays_date = str(datetime.now())

import dataclasses
import re
import sys
import typing
from typing import Optional, Tuple, Union

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Draw

import doranet
from doranet import interfaces, metadata

print(f"Last update on {todays_date}")
print(sys.version)
print("rdkit version: ", Chem.rdBase.rdkitVersion)

## Initialize doranet engine
engine = doranet.create_engine()
network = engine.new_network()


def print_time(time_end, time_start):
    if time_end - time_start > 120:  # more than 120 seconds (~ 2 min)
        print(f"Executed in {(time_end - time_start)/60:.3f} min")
    else:
        print(f"Executed in {(time_end - time_start):.3f} sec")


def update_isotope_smiles(
    input_string: str = None,
    special_species_list_not_to_update_isotope: list = None,
):
    if special_species_list_not_to_update_isotope is None:
        special_species_list_not_to_update_isotope = ["O=O"]

    if input_string in special_species_list_not_to_update_isotope:
        output_string = input_string
    else:
        input_string_addHs = Chem.MolToSmiles(
            Chem.AddHs(Chem.MolFromSmiles(input_string))
        )

        def Hydrogen_Count(match):
            nonlocal hydrogen_counter
            hydrogen_counter += 1
            return f"[{hydrogen_counter}H]"

        hydrogen_counter = 0
        output_string = re.sub(r"\[H\]", Hydrogen_Count, input_string_addHs)

    return output_string


def canonical_smiles_parsing(
    input_string: str = None, visualize_mol: bool = None
):
    output_string = re.sub(r"\[(\d+)H\]", r"[H]", input_string)
    output_string = Chem.RemoveHs(Chem.MolFromSmiles(output_string))

    def show_atom_number(mol, label="atomNote", figsize=(300, 200)):
        for atom in mol.GetAtoms():
            atom.SetProp(label, str(atom.GetIdx()))

        AllChem.Compute2DCoords(mol)
        display(Draw.MolToImage(mol, size=figsize))

    if visualize_mol:
        show_atom_number(output_string)

    return Chem.MolToSmiles(output_string)


def write_to_file(
    output_to_save: list | dict | tuple = None, file_path: str = None
):
    if isinstance(output_to_save, list | tuple):
        with open(file_path, "w") as txt_file:
            for idx, value in enumerate(output_to_save):
                txt_file.write(str(value) + "\n")

    elif isinstance(output_to_save, dict):
        with open(file_path, "w") as txt_file:
            for idx, value in output_to_save.items():
                if len(output_to_save) < 1e5:
                    txt_file.write(f"{idx:<7}" + str(value) + "\n")
                elif len(output_to_save) < 1e8:
                    txt_file.write(f"{idx:<10}" + str(value) + "\n")
                elif len(output_to_save) < 1e11:
                    txt_file.write(f"{idx:<13}" + str(value) + "\n")
                elif len(output_to_save) < 1e14:
                    txt_file.write(f"{idx:<17}" + str(value) + "\n")
                elif len(output_to_save) > 1e14:
                    txt_file.write(f"{idx:<25}" + str(value) + "\n")


def write_rxn(reaction_data_list: list = None):
    _rxn_info, rxn_output = [], []

    for i in reaction_data_list:
        reactants_list = [str(i) for i in i[0]]
        prod_list = [str(i) for i in i[1]]
        rxn_abbrev = i[2]

        if len(reactants_list) > 1:
            reactant_text = ", ".join(reactants_list)
        else:
            reactant_text = reactants_list[0]

        if len(prod_list) > 1:
            product_text = ", ".join(prod_list)
        else:
            product_text = prod_list[0]

        rxn_output.append(f"{reactant_text} : {product_text} : {rxn_abbrev} ;")

    return rxn_output


@typing.final
@dataclasses.dataclass(frozen=True)
class RadicalPosition(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        for idx, mol in enumerate(recipe.reactants):
            if (
                Chem.Descriptors.NumRadicalElectrons(mol.item.rdkitmol)
                != recipe.operator.meta["radical_tuple"][idx]
            ):
                return False
        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"radical_tuple"})


@typing.final
@dataclasses.dataclass(frozen=True)
class OxygenAppearance(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if recipe.operator.meta["oxygen_presence_tuple"] is not None:
            for idx, mol in enumerate(recipe.reactants):
                if (
                    recipe.operator.meta["oxygen_presence_tuple"][idx]
                    is not None
                ) and (
                    mol.meta["oxygen_presence"]
                    != recipe.operator.meta["oxygen_presence_tuple"][idx]
                ):
                    return False
        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"oxygen_presence_tuple"})


@typing.final
@dataclasses.dataclass(frozen=True)
class ComparingCarbonChainLength(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if (
            recipe.operator.meta["C_atom_check"] is not None
            and (
                len(set([mol.meta["carbon_num"] for mol in recipe.reactants]))
                == 1
            )
            and (recipe.operator.meta["C_atom_check"] is True)
        ):
            return False

        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"C_atom_check"})


@typing.final
@dataclasses.dataclass(frozen=True)
class CalculateCarbonChainLength(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if recipe.operator.meta["max_permit_carbon"] is not None:
            for idx, mol in enumerate(recipe.reactants):
                if (
                    recipe.operator.meta["max_permit_carbon"][idx] is not None
                ) and (
                    mol.meta["carbon_num"]
                    >= recipe.operator.meta["max_permit_carbon"][idx] + 1
                ):
                    return False
        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"max_permit_carbon"})


@typing.final
@dataclasses.dataclass(frozen=True)
class CheckOxygenNumberReactants(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if recipe.operator.meta["OXY_ABSTRACT_COUNT"] is not None:
            for idx, mol in enumerate(recipe.reactants):
                if recipe.operator.meta["OXY_ABSTRACT_COUNT"][idx] is not None:
                    if (
                        mol.meta["oxygen_num"]
                        >= recipe.operator.meta["OXY_ABSTRACT_COUNT"][idx] + 1
                    ):
                        return False
        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"OXY_ABSTRACT_COUNT"})


@typing.final
@dataclasses.dataclass(frozen=True)
class CheckSpeciesSimilarity(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if recipe.operator.meta["species_similarity_check"] is not None:
            reactant_list = sorted(
                list(
                    set(
                        [
                            canonical_smiles_parsing(
                                recipe.reactants[idx].item.uid
                            )
                            for idx, _ in enumerate(recipe.reactants)
                        ]
                    )
                )
            )
            products_list = sorted(
                list(
                    set(
                        [
                            canonical_smiles_parsing(
                                recipe.products[idx].item.uid
                            )
                            for idx, _ in enumerate(recipe.products)
                        ]
                    )
                )
            )

            if products_list == reactant_list:
                return False

        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(
            operator_keys={"species_similarity_check"}
        )


@typing.final
@dataclasses.dataclass(frozen=True)
class CheckSpeciesMoeity(metadata.ReactionFilterBase):
    def __call__(self, recipe: interfaces.ReactionExplicit) -> bool:
        if recipe.operator.meta["species_moeity_check"] is not None:
            for idx, _mol in enumerate(recipe.products):
                for moeity in recipe.operator.meta["species_moeity_check"]:
                    product_smi = canonical_smiles_parsing(
                        recipe.products[idx].item.uid
                    )
                    if (
                        Chem.MolFromSmiles(product_smi).HasSubstructMatch(
                            Chem.MolFromSmarts(moeity)
                        )
                        is True
                    ):
                        return False
        return True

    @property
    def meta_required(self) -> interfaces.MetaKeyPacket:
        return interfaces.MetaKeyPacket(operator_keys={"species_moeity_check"})


MAX_C_ATOM = 10
MAX_O_ATOM = 2


@dataclasses.dataclass(frozen=True, slots=True)
class custom_operator_rxn_smarts:
    name: str = None
    rxn_smarts: str = None
    radical_tuple: Optional[tuple[int, ...]] = None
    generation_tuple: Optional[tuple[int, ...]] = None
    oxygen_presence_tuple: Optional[Tuple[Union[bool, None]]] = None
    C_atom_check: Optional[Union[bool, None]] = None
    max_permit_carbon: Optional[Tuple[Union[bool, None]]] = None
    OXY_ABSTRACT_COUNT: Optional[
        Tuple[Union[bool, int, float, None]] | Union[bool, int, float, None]
    ] = None
    species_similarity_check: Optional[bool] = None
    species_moeity_check: Optional[str] = None
    id_position_check: Optional[Union[str, bool, None]] = None
    substrate_selection_check: Optional[
        Union[bool, None] | Tuple[Union[bool, None]]
    ] = None


operator_smarts = (
    # 1 Primary Initation
    custom_operator_rxn_smarts(
        name="oxyinit",  # RH + O2 --> R. + HOO.
        rxn_smarts="[C:1][H:2].[O+0:3]=[O+0:4]>>[*H0:1].[H:2][*:3][*H0:4]",
        radical_tuple=(0, 0),
        C_atom_check=True,
        max_permit_carbon=(MAX_C_ATOM, None),
        substrate_selection_check=(True, None),
    ),
    # 2 Bond Fission
    custom_operator_rxn_smarts(
        name="init",
        rxn_smarts="[C+0:2][O:3][O+0H:4]>>[*:2][*H0:3].[*H0:4]",
        radical_tuple=(0,),
        oxygen_presence_tuple=(True,),
        max_permit_carbon=(MAX_C_ATOM,),
    ),
    # 2 Hydroperoxide Decomposition
    custom_operator_rxn_smarts(
        name="hpdecomp",
        rxn_smarts="[C:1][O:2][OX2+0H:3].[C:4][H:5]>>[*:1][*H0:2].[*:3][H:5].[*H0:4]",
        radical_tuple=(0, 0),
        C_atom_check=False,
        substrate_selection_check=(None, True),
    ),
    # 4 Oxygen Addition
    custom_operator_rxn_smarts(
        name="oxygadd",
        rxn_smarts="[Cv3:1].[O:2]=[O:3]>>[*:1][*:2][*H0:3]",
        radical_tuple=(1, 0),
    ),
    # Type: beta_scission_from_alkoxy_rxn
    custom_operator_rxn_smarts(
        name="oxybscission",
        rxn_smarts="[OX1:1][C:2][C+0:3]>>[*:1]=[*:2].[*H0:3]",
        radical_tuple=(1,),
        oxygen_presence_tuple=(True,),
    ),
    custom_operator_rxn_smarts(
        name="oxybscission",
        rxn_smarts="[C+0:1][O:2][OX1:3]>>[*:2]=[*:3].[*H0:1]",
        radical_tuple=(1,),
        oxygen_presence_tuple=(True,),
    ),
    # beta_scission_from_C_centered_radical_rxn
    custom_operator_rxn_smarts(
        name="bscission",
        rxn_smarts="[Cv3:1][O:2][O+0H:3]>>[*:1]=[*:2].[*H0:3]",
        radical_tuple=(1,),
        oxygen_presence_tuple=(True,),
    ),
    custom_operator_rxn_smarts(
        name="bscission",
        rxn_smarts="[Cv3:1][O:2][OX2+0:3]>>[*:1]=[*:2].[*H0:3]",
        radical_tuple=(1,),
        oxygen_presence_tuple=(True,),
    ),
    # hydrogen_transfer_habsOxy_rxn
    custom_operator_rxn_smarts(
        name="habsOxy",
        rxn_smarts="[H:5][C+0:1][H:2].[C:3][OX1:4]>>[*H0:1][H:2].[*:3][*:4][H:5]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(None, True),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
    ),
    # hydrogen_transfer_alkylperoxy_radical_and_alkane_rxn
    custom_operator_rxn_smarts(
        name="habsPOxy",
        rxn_smarts="[H:6][C+0:1][H:2].[C:3][O:4][OX1:5]>>[*H0:1][H:2].[*:3][*:4][*:5][H:6]",
        radical_tuple=(0, 1),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
        species_moeity_check=[
            "[*:1][CH2:2][CH0:3]=[O:4]",
            "[CH0:1][O:2][OH1:3]",
            "[*:1][CH1:2][O:3][OH1:4]",
            "[*:1][CH1:1][C:2](=[O:3])[CH2:4][*:5]",
        ],
    ),
    # hydrogen_transfer_alkylperoxy_radical_and_aldehydes_rxn
    custom_operator_rxn_smarts(
        name="habsPCOxy",
        rxn_smarts="[C:1][O+0:2][O+0X1:3].[CX3+0:4]([H:6])=[O+0:5]>>[*:1][*:2][*:3][H:6].[*H0:4]=[*:5]",
        radical_tuple=(1, 0),
        oxygen_presence_tuple=(True, True),
        OXY_ABSTRACT_COUNT=(None, MAX_O_ATOM),
        species_similarity_check=True,
    ),
    # hydrogen_transfer_alkylperoxy_radical_and_alkyl_hydroperoxides_rxn
    custom_operator_rxn_smarts(
        name="habsKET",
        rxn_smarts="[C+0:2]([H:8])[O:3][O+0H:4].[C:5][O:6][OX1H0:7]>>[*H0:2][*:3][*:4].[*:5][*:6][*:7][*:8]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(True, True),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
    ),
    # hydrogen transfer adjacent to a CO group in ketones
    custom_operator_rxn_smarts(
        name="habsKET2",
        rxn_smarts="[C+0:1]([H:7])[C:2](=[O:3])[C:8].[C:4][O:5][OX1H0:6]>>[*H0:1][*:2](=[*:3])[*:8].[*:4][*:5][*:6][H:7]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(True, True),
        max_permit_carbon=(None, None),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
        species_moeity_check=["CCC(=O)[CH2]", "C[CH]C=O"],
    ),
    custom_operator_rxn_smarts(
        name="habsKET2",
        rxn_smarts="[C+0:1]([H:6])[C:2](=[O:3])[C:7].[C:4][OX1H0:5]>>[*H0:1][*:2](=[*:3])[*:7].[*:4][*:5][H:6]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(True, True),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
        species_moeity_check=["CCC(=O)[CH2]", "C[CH]C=O"],
    ),
    # Other types of H-abstraction
    custom_operator_rxn_smarts(
        name="habs",
        rxn_smarts="[C,O,H0:1][O+0:2][H:5].[C,O,H0:3][OX1:4]>>[*:1][*H0:2].[*:3][*:4][H:5]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(None, True),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
    ),
    custom_operator_rxn_smarts(
        name="habs",
        rxn_smarts="[#6;H1,H2,O+0:1][H:2].[O+0H,!O;!C:3][Ov1+0:4]>>[*H0:1].[*:3][*:4][H:2]",
        radical_tuple=(0, 1),
        oxygen_presence_tuple=(None, True),
        OXY_ABSTRACT_COUNT=(MAX_O_ATOM, None),
        species_similarity_check=True,
    ),
    # Disproportionation (Type A)
    custom_operator_rxn_smarts(
        name="perdispropcross",
        rxn_smarts="[C:1]([H:7])[O:2][OX1:3].[C:4][O:5][OX1:6]>>[*:4][*:5][H:7].[*:1]=[*:2].[O:3]=[O:6]",
        radical_tuple=(1, 1),
        oxygen_presence_tuple=(True, True),
        id_position_check=None,
    ),
    custom_operator_rxn_smarts(
        name="perdispropcross",
        rxn_smarts="[C:1]([H:6])[O:2][OX1:3].[Ov1+0:4][O+0H:5]>>[*:5][H:6].[*:1]=[*:2].[O:3]=[O:4]",
        radical_tuple=(1, 1),
        oxygen_presence_tuple=(True, True),
    ),
    # Disproportionation (Type B) type 1
    custom_operator_rxn_smarts(
        name="perdisprop2ho2",
        rxn_smarts="[O+0H:1][Ov1+0:2].[Ov1+0:3][O+0H:4]>>[*H0:1].[O:2]=[O:3].[*H0:4]",
        radical_tuple=(1, 1),
        oxygen_presence_tuple=(True, True),
        OXY_ABSTRACT_COUNT=None,
    ),
    custom_operator_rxn_smarts(
        name="perdisprop2ho2",
        rxn_smarts="[C:1][O:2][OX1:3].[Ov1+0:4][O+0H:5]>>[*:1][*H0:2].[*:3]=[*:4].[*H0:5]",
        radical_tuple=(1, 1),
        oxygen_presence_tuple=(True, True),
        OXY_ABSTRACT_COUNT=None,
    ),
    # Disproportionation (Type B) type 2
    custom_operator_rxn_smarts(
        name="perdisprop2",
        rxn_smarts="[C:1][O:2][OX1:3].[C:4][O:5][OX1:6]>>[*:1][*H0:2].[O:3]=[O:6].[*:4][*H0:5]",
        radical_tuple=(1, 1),
        oxygen_presence_tuple=(True, True),
        id_position_check=None,
        OXY_ABSTRACT_COUNT=None,
    ),
    # Recombination
    custom_operator_rxn_smarts(
        name="recomb",
        rxn_smarts="[C,O,H0:1][OX1:2].[C,O,H0:3][OX1:4]>>[*:1][*:2][*:4][*:3]",
        radical_tuple=(1, 1),
        max_permit_carbon=(MAX_C_ATOM, MAX_C_ATOM),
        species_moeity_check=[
            "COOOC",
            "COOO",
            "OOO",
            "COOOOC",
            "COOOO",
            "OOOO",
        ],
        id_position_check=None,
    ),
    custom_operator_rxn_smarts(
        name="recomb",
        rxn_smarts="[C,O,H0:1][OX1:2].[Cv3:3]>>[*:1][*:2][*:3]",
        radical_tuple=(1, 1),
        max_permit_carbon=(MAX_C_ATOM, MAX_C_ATOM),
        species_moeity_check=[
            "COOOC",
            "COOO",
            "OOO",
            "COOOOC",
            "COOOO",
            "OOOO",
        ],
    ),
    custom_operator_rxn_smarts(
        name="recomb",
        rxn_smarts="[Cv3:1].[Cv3:2]>>[*:1][*:2]",
        radical_tuple=(1, 1),
        max_permit_carbon=(MAX_C_ATOM, MAX_C_ATOM),
        id_position_check=None,
    ),
    custom_operator_rxn_smarts(
        name="recomb",
        rxn_smarts="[Cv3:1]=[O:2].[O+0H,!O;!C:3][Ov1+0:4]>>[*:1](=[O:2])[*:4][*:3]",
        radical_tuple=(1, 1),
        max_permit_carbon=(MAX_C_ATOM, None),
    ),
    # 17 Bayer-Villiger
    custom_operator_rxn_smarts(
        name="BV",
        rxn_smarts="[CX3+0:1]([H:7])=[O+0:2].[CX3:3](=[O+0:4])[O:5][O+0H:6]>>[*:1](=[O:2])[*:5].[*:3](=[O:4])[*:6]",
        radical_tuple=(0, 0),
        oxygen_presence_tuple=(True, True),
        C_atom_check=True,
    ),
)


initial_reactant_smiles = [
    update_isotope_smiles("CCCC"),
    update_isotope_smiles("O=O"),
]

for smiles in initial_reactant_smiles:
    network.add_mol(
        engine.mol.rdkit(smiles),
        meta={
            "gen": 0,
            "radical_num": Descriptors.NumRadicalElectrons(
                Chem.MolFromSmiles(canonical_smiles_parsing(smiles))
            ),
            "oxygen_presence": "O"
            in [
                atom.GetSymbol()
                for atom in Chem.MolFromSmiles(smiles).GetAtoms()
            ],
        },
    )

for smarts in operator_smarts:
    network.add_op(
        engine.op.rdkit(smarts.rxn_smarts),
        meta={
            "name": smarts.name,
            "rxn_smarts": smarts.rxn_smarts,
            "radical_tuple": smarts.radical_tuple,
            "generation_tuple": smarts.generation_tuple,
            "oxygen_presence_tuple": smarts.oxygen_presence_tuple,
            "C_atom_check": smarts.C_atom_check,
            "max_permit_carbon": smarts.max_permit_carbon,
            "OXY_ABSTRACT_COUNT": smarts.OXY_ABSTRACT_COUNT,
            "species_similarity_check": smarts.species_similarity_check,
            "species_moeity_check": smarts.species_moeity_check,
            "id_position_check": smarts.id_position_check,
        },
    )

max_iteration = 2

network.save_to_file("dummy_test")
network = engine.network_from_file("dummy_test")
strat = engine.strat.cartesian(network)
final_rank = 1
atom_num = [atom.GetAtomicNum() for atom in Chem.MolFromSmiles("C").GetAtoms()]

gen_filter = engine.filter.reaction.generation(final_rank, "gen")
max_atoms_filter = engine.filter.reaction.max_atoms(
    max_atoms=MAX_C_ATOM, proton_number=atom_num[0]
)

reaction_plan = (
    engine.meta.generation("gen")  # generation (i.e., rank)
)

strat.expand(
    num_iter=max_iteration,
    reaction_plan=reaction_plan,
    save_unreactive=False,
)

print("wow")
