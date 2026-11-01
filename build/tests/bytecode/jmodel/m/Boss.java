package m;
import net.minecraft.client.model.geom.builders.*;
import net.minecraft.client.model.geom.PartPose;
public class Boss {
  public static LayerDefinition createBodyLayer() {
    MeshDefinition mesh = new MeshDefinition();
    PartDefinition root = mesh.m_171576_();
    PartDefinition body = root.m_171599_("body", CubeListBuilder.m_171558_().m_171514_(0, 0).m_171481_(-4, 0, -2, 8, 12, 4), PartPose.m_171419_(0, 12, 0));
    for (int i = 0; i < 4; i++) {
      body.m_171599_("leg" + i, CubeListBuilder.m_171558_().m_171514_(0, 16).m_171481_(-1, 0, -1, 2, 6, 2), PartPose.m_171419_(i * 2 - 3, 6, 0));
    }
    root.m_171599_("tail", CubeListBuilder.m_171558_().m_171481_(-1, 0, 0, 2, 2, 6), PartPose.m_171423_(0, 10, 2, (float)Math.toRadians(30), 0, 0.5f));
    int seg = 3;
    root.m_171599_("neck", CubeListBuilder.m_171558_().m_171481_(-1, -1, -1, seg / 2, 2, 2), PartPose.m_171419_(0, 4, 0));
    return LayerDefinition.m_171565_(mesh, 64, 32);
  }
}
