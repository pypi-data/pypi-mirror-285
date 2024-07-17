import doranet

engine = doranet.create_engine()
network = engine.new_network()
network.add_mol(engine.mol.rdkit("C#C"), meta={"gen": 0})
network.add_op(engine.op.rdkit("[C:1]#[C:2]>>[*:1]=[*:2]"))
network.add_op(engine.op.rdkit("[C:1]#[C:2]>>[*:1]-[*:2]"))
network.add_op(engine.op.rdkit("[C:1]=[C:2]>>[*:1]-[*:2]"))

strat = engine.strat.cartesian(network)

strat.expand(reaction_plan=doranet.metacalc.GenerationCalculator("gen"))

print("testo")
